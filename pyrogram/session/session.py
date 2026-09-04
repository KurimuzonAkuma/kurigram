#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

import asyncio
import bisect
import logging
import os
from enum import Enum, auto
from hashlib import sha1
from io import BytesIO
from typing import Any, Coroutine, Dict, List, Optional, Set

import pyrogram
from pyrogram import raw, utils
from pyrogram.connection import Connection
from pyrogram.connection.proxy import client_proxy_address
from pyrogram.crypto import mtproto
from pyrogram.errors import (
    AuthKeyDuplicated,
    BadMsgNotification,
    FloodPremiumWait,
    FloodWait,
    InternalServerError,
    RPCError,
    SecurityCheckMismatch,
    ServiceUnavailable,
    Unauthorized,
)
from pyrogram.raw.all import layer
from pyrogram.raw.core import FutureSalts, Int, MsgContainer, TLObject

from .internals import MsgFactory

log = logging.getLogger(__name__)


class SessionState(Enum):
    STARTING = auto()
    STARTED = auto()
    STOPPING = auto()
    STOPPED = auto()


class TransportError(Exception):
    pass


class AuthKeyNotFound(TransportError):
    pass


class TransportFlood(TransportError):
    pass


class InvalidDC(TransportError):
    pass


class Result:
    __slots__ = ("value", "event")

    def __init__(self):
        self.value: Any = None
        self.event: asyncio.Event = asyncio.Event()


class Session:
    START_TIMEOUT = 2
    STOP_TIMEOUT = 2
    WAIT_TIMEOUT = 15
    SLEEP_THRESHOLD = 10
    MAX_RETRIES = 10
    ACKS_THRESHOLD = 10
    PING_INTERVAL = 5
    RETRY_DELAY = 1
    STORED_MSG_IDS_MAX_SIZE = 1000 * 2
    CRYPTO_EXECUTOR_WORKERS = 1
    MAX_CONSECUTIVE_IGNORED = 30

    def __init__(
        self,
        client: "pyrogram.Client",
        dc_id: int,
        server_address: str,
        port: int,
        auth_key: bytes,
        test_mode: bool,
        is_media: bool = False,
        is_cdn: bool = False,
    ):
        self.client = client
        self.dc_id = dc_id
        self.server_address = server_address
        self.port = port
        self.auth_key = auth_key
        self.test_mode = test_mode
        self.is_media = is_media
        self.is_cdn = is_cdn

        self.connection: Optional[Connection] = None

        self._state = SessionState.STOPPED
        self._state_lock = asyncio.Lock()

        self.auth_key_id = sha1(auth_key).digest()[-8:]

        self.session_id = os.urandom(8)
        self.msg_factory = MsgFactory(self.client)

        self.salt = 0

        self.ignore_count = 0

        self.pending_acks: Set[int] = set()

        self.results: Dict[int, Result] = {}

        self.stored_msg_ids: List[int] = []
        self.recent_msg_ids: List[int] = []

        self.ping_task: Optional[asyncio.Task] = None
        self.ping_task_event = asyncio.Event()

        self.recv_task: Optional[asyncio.Task] = None

        self.pending_tasks: Set[asyncio.Task] = set()

        self.is_started = asyncio.Event()
        self.restart_lock = asyncio.Lock()

        # Never cleared: a stopped session is replaced rather than started again, since
        #  every caller that stops one then asks for a new one (`pyrogram/client.py:1428`).
        self._must_stay_stopped: bool = False

    @property
    def state(self) -> SessionState:
        """Get current session state"""
        return self._state

    async def _set_state(self, new_state: SessionState) -> None:
        """Set session state"""
        async with self._state_lock:
            old_state = self._state
            self._state = new_state

            log.debug("Session state changed: %s -> %s", old_state.name, new_state.name)

    def _create_tracked_task(self, coroutine: Coroutine[Any, Any, Any]) -> asyncio.Task:
        # The set is what `stop()` waits on, and it is also the strong reference the
        #  loop does not hold: an unreferenced task can be collected mid-execution.
        #  https://docs.python.org/3/library/asyncio-task.html#creating-tasks
        task = self.client.loop.create_task(coroutine)

        self.pending_tasks.add(task)
        task.add_done_callback(self.pending_tasks.discard)

        return task

    async def _wait_pending_tasks(self) -> None:
        # A tracked `handle_packet` spawns a tracked `handle_updates`, so one round can
        #  leave a task behind. Every level is already running, so the loop ends.
        while self.pending_tasks:
            round_tasks = set(self.pending_tasks)
            _, running = await asyncio.wait(round_tasks, timeout=self.STOP_TIMEOUT)

            # `invoke` first waits `WAIT_TIMEOUT` for `is_started`, which stopping has
            #  just cleared, and then another one for an answer that is not coming, so
            #  a task caught mid-request would hold the shutdown for half a minute.
            for task in running:
                task.cancel()

            for result in await asyncio.gather(*round_tasks, return_exceptions=True):
                if isinstance(result, Exception):
                    log.error("Task failed while the session was stopping", exc_info=result)

    async def start(self):
        if self._state in (SessionState.STARTED, SessionState.STARTING):
            log.debug("Session already started")
            return

        await self._set_state(SessionState.STARTING)

        self.connection = self.client.connection_factory(
            dc_id=self.dc_id,
            server_address=self.server_address,
            port=self.port,
            test_mode=self.test_mode,
            proxy=self.client.proxy,
            media=self.is_media,
            protocol_factory=self.client.protocol_factory,
            crypto_executor_workers=self.CRYPTO_EXECUTOR_WORKERS,
            loop=self.client.loop
        )

        try:
            await self.connection.connect()

            self.recv_task = self.client.loop.create_task(self.recv_worker())

            await self.send(raw.functions.Ping(ping_id=0), timeout=self.START_TIMEOUT)

            init_connection_params = self.client.init_connection_params

            # Telegram wants to know which proxy a client sits behind.
            proxy_address = client_proxy_address(self.client.proxy)
            client_proxy: Optional[raw.types.InputClientProxy] = None

            if proxy_address is not None:
                client_proxy = raw.types.InputClientProxy(
                    address=proxy_address.hostname,
                    port=proxy_address.port,
                )

            if isinstance(init_connection_params, dict):
                init_connection_params = utils.obj_to_jsonvalue(init_connection_params)

            if not self.is_cdn:
                await self.send(
                    raw.functions.InvokeWithLayer(
                        layer=layer,
                        query=raw.functions.InitConnection(
                            api_id=await self.client.storage.api_id(),
                            app_version=self.client.app_version,
                            device_model=self.client.device_model,
                            system_version=self.client.system_version,
                            system_lang_code=self.client.system_lang_code,
                            lang_pack=self.client.lang_pack,
                            lang_code=self.client.lang_code,
                            query=raw.functions.help.GetConfig(),
                            params=init_connection_params,
                            proxy=client_proxy,
                        )
                    ),
                    timeout=self.START_TIMEOUT
                )

            self.ping_task = self.client.loop.create_task(self.ping_worker())

            log.info(
                "Session initialized: Pyrogram v%s (Layer %s)", pyrogram.__version__, layer
            )
            log.info("Device: %s - %s", self.client.device_model, self.client.app_version)
            log.info("System: %s (%s)", self.client.system_version, self.client.lang_code)
        except (AuthKeyDuplicated, Unauthorized) as e:
            await self.stop()
            raise e
        except (OSError, RPCError) as e:
            log.info("Restarting session due to - %s - %s", e.__class__.__name__, e)
            self.client.loop.create_task(self.restart())
            return
        except Exception as e:
            await self.stop()
            raise e

        await self._set_state(SessionState.STARTED)
        self.is_started.set()

        log.info("Session started")

        if callable(self.client.connect_handler):
            try:
                await self.client.connect_handler(self.client, self)
            except Exception as e:
                log.exception(e)

    async def stop(self):
        # `restart()` reads this, and the flag is set before the state check below so a
        #  stop that arrives while a restart is already between its own `stop()` and
        #  `start()` still counts.
        self._must_stay_stopped = True

        await self._stop()

    async def _stop(self) -> None:
        if self._state in (SessionState.STOPPED, SessionState.STOPPING):
            log.debug("Session already stopped")
            return

        await self._set_state(SessionState.STOPPING)

        self.ignore_count = 0

        self.is_started.clear()

        self.stored_msg_ids.clear()

        self.ping_task_event.set()

        if self.ping_task is not None:
            await self.ping_task

        self.ping_task_event.clear()

        await self.connection.close()

        if self.recv_task:
            await self.recv_task
            self.recv_task = None

        await self._wait_pending_tasks()

        await self._set_state(SessionState.STOPPED)

        log.info("Session stopped")

        if callable(self.client.disconnect_handler):
            try:
                await self.client.disconnect_handler(self.client, self)
            except Exception as e:
                log.exception(e)

    async def restart(self):
        async with self.restart_lock:
            if self.stored_msg_ids:
               self.recent_msg_ids = self.stored_msg_ids[:30]

            await self._stop()

            if self._must_stay_stopped:
                return

            await self.start()

            # `stop()` does not take `restart_lock`, because `start()` calls `stop()` on
            #  failure and would deadlock on it. So a stop landing inside `start()` is
            #  undone here rather than prevented.
            if self._must_stay_stopped:
                await self._stop()

    async def handle_packet(self, packet):
        try:
            data = await self.client.loop.run_in_executor(
                self.connection.protocol.crypto_executor,
                mtproto.unpack,
                BytesIO(packet),
                self.session_id,
                self.auth_key,
                self.auth_key_id
            )
        except ValueError as e:
            log.debug(e)
            log.info("Restarting session due to - %s - %s", e.__class__.__name__, e)
            self.client.loop.create_task(self.restart())
            return

        messages = (
            data.body.messages
            if isinstance(data.body, MsgContainer)
            else [data]
        )

        log.debug("Received: %s", data)

        for msg in messages:
            if msg.seq_no == 0:
                self.client._set_server_time(msg.msg_id)

            if msg.seq_no % 2 != 0:
                if msg.msg_id in self.pending_acks:
                    continue
                else:
                    self.pending_acks.add(msg.msg_id)

            try:
                if len(self.stored_msg_ids) > Session.STORED_MSG_IDS_MAX_SIZE:
                    del self.stored_msg_ids[:Session.STORED_MSG_IDS_MAX_SIZE // 2]

                if msg.msg_id in self.recent_msg_ids:
                   self.recent_msg_ids.remove(msg.msg_id)
                   raise SecurityCheckMismatch(
                         "The msg_id is belong to most recent closed connection."
                   )

                if self.stored_msg_ids:
                    if msg.msg_id < self.stored_msg_ids[0]:
                        raise SecurityCheckMismatch(
                            "The msg_id is lower than all the stored values"
                        )

                    if msg.msg_id in self.stored_msg_ids:
                        raise SecurityCheckMismatch(
                            "The msg_id is equal to any of the stored values"
                        )

                    time_diff = (msg.msg_id - (await self.msg_factory.allocate_message_identity())) / 2 ** 32

                    if time_diff > 30:
                        raise SecurityCheckMismatch(
                            "The msg_id belongs to over 30 seconds in the future. "
                            "Most likely the client time has to be synchronized."
                        )

                    if time_diff < -300:
                        raise SecurityCheckMismatch(
                            "The msg_id belongs to over 300 seconds in the past. "
                            "Most likely the client time has to be synchronized."
                        )

                    self.ignore_count = 0
            except SecurityCheckMismatch as e:
                log.info("Discarding packet: %s", e)

                self.ignore_count += 1

                if self.ignore_count >= self.MAX_CONSECUTIVE_IGNORED:
                    log.info("Restarting session due to - %s - %s", e.__class__.__name__, e)
                    self.client.loop.create_task(self.restart())

                return
            else:
                bisect.insort(self.stored_msg_ids, msg.msg_id)

            if isinstance(msg.body, (raw.types.MsgDetailedInfo, raw.types.MsgNewDetailedInfo)):
                self.pending_acks.add(msg.body.answer_msg_id)
                continue

            if isinstance(msg.body, raw.types.NewSessionCreated):
                continue

            msg_id = None

            if isinstance(msg.body, (raw.types.BadMsgNotification, raw.types.BadServerSalt)):
                msg_id = msg.body.bad_msg_id
            elif isinstance(msg.body, (FutureSalts, raw.types.RpcResult)):
                msg_id = msg.body.req_msg_id
            elif isinstance(msg.body, raw.types.Pong):
                msg_id = msg.body.msg_id
            else:
                if self.client is not None:
                    self._create_tracked_task(self.client.handle_updates(msg.body))

            if msg_id in self.results:
                self.results[msg_id].value = getattr(msg.body, "result", msg.body)
                self.results[msg_id].event.set()

        if len(self.pending_acks) >= self.ACKS_THRESHOLD:
            log.debug("Sending %s acks", len(self.pending_acks))

            try:
                await self.send(raw.types.MsgsAck(msg_ids=list(self.pending_acks)), False)
            except OSError:
                pass
            else:
                self.pending_acks.clear()

    async def ping_worker(self):
        log.info("PingTask started")

        while True:
            try:
                await asyncio.wait_for(self.ping_task_event.wait(), self.PING_INTERVAL)
            except asyncio.TimeoutError:
                pass
            else:
                break

            try:
                await self.send(
                    raw.functions.PingDelayDisconnect(
                        ping_id=await self.msg_factory.allocate_message_identity(),
                        disconnect_delay=self.WAIT_TIMEOUT + 10
                    ),
                    wait_response=False
                )
            except OSError as e:
                log.info("Restarting session due to - %s - %s", e.__class__.__name__, e)
                self.client.loop.create_task(self.restart())
                break
            except RPCError:
                pass

        log.info("PingTask stopped")

    async def recv_worker(self):
        log.info("NetworkTask started")

        while True:
            packet = await self.connection.recv()

            if packet is None or len(packet) == 4:
                if packet:
                    error_code = -Int.read(BytesIO(packet))
                    error_msg = "unknown error"

                    if error_code == 404:
                        raise AuthKeyNotFound(
                            "Auth key not found in the system. Try again or delete your session file "
                            "and log in again with your phone number or bot token."
                        )

                    try:
                        if error_code == 429:
                            raise TransportFlood(
                                "Transport flood. Please slow down your requests."
                            )
                        elif error_code == 444:
                            raise InvalidDC(
                                "Invalid data center. Please check your configuration."
                            )
                    except TransportError as e:
                        error_msg = str(e)

                    log.warning("Server sent transport error: %s (%s)", error_code, error_msg)


                if self.is_started.is_set():
                    if packet:
                        error = f"Server sent transport error - {error_code} - ({error_msg})."
                    else:
                        error = "Server sent a null packet."

                    log.info("Restarting session due to - %s", error)
                    self.client.loop.create_task(self.restart())

                break

            self._create_tracked_task(self.handle_packet(packet))

        log.info("NetworkTask stopped")

    async def send(
        self, data: TLObject, wait_response: bool = True, timeout: float = WAIT_TIMEOUT
    ):
        message = await self.msg_factory.create(data)
        msg_id = message.msg_id

        if wait_response:
            self.results[msg_id] = Result()

        log.debug("Sent: %s", message)

        payload = await self.client.loop.run_in_executor(
            self.connection.protocol.crypto_executor,
            mtproto.pack,
            message,
            self.salt,
            self.session_id,
            self.auth_key,
            self.auth_key_id
        )

        try:
            await self.connection.send(payload)
        except OSError as e:
            self.results.pop(msg_id, None)
            raise e

        if wait_response:
            try:
                await asyncio.wait_for(self.results[msg_id].event.wait(), timeout)
            except asyncio.TimeoutError:
                pass

            result = self.results.pop(msg_id).value

            if result is None:
                raise TimeoutError("Request timed out")

            if isinstance(result, raw.types.RpcError):
                if isinstance(
                    data, (raw.functions.InvokeWithoutUpdates, raw.functions.InvokeWithTakeout)
                ):
                    data = data.query

                RPCError.raise_it(result, type(data))

            if isinstance(result, raw.types.BadMsgNotification):
                log.warning(
                    "%s: %s", BadMsgNotification.__name__, BadMsgNotification(result.error_code)
                )

            if isinstance(result, raw.types.BadServerSalt):
                self.salt = result.new_server_salt
                return await self.send(data, wait_response, timeout)

            return result

    async def invoke(
        self,
        query: TLObject,
        retries: int = MAX_RETRIES,
        timeout: float = WAIT_TIMEOUT,
        sleep_threshold: float = SLEEP_THRESHOLD,
        retry_delay: float = RETRY_DELAY
    ):
        try:
            await asyncio.wait_for(self.is_started.wait(), self.WAIT_TIMEOUT)
        except asyncio.TimeoutError:
            pass

        if isinstance(
            query, (raw.functions.InvokeWithoutUpdates, raw.functions.InvokeWithTakeout)
        ):
            inner_query = query.query
        else:
            inner_query = query

        query_name = ".".join(inner_query.QUALNAME.split(".")[1:])

        for attempt in range(1, retries + 1):
            try:
                return await self.send(query, timeout=timeout)
            except (FloodWait, FloodPremiumWait) as e:
                amount = e.seconds

                if amount > sleep_threshold >= 0:
                    raise

                log.warning(
                    '[%s] Waiting for %s seconds before continuing (required by "%s")',
                    self.client.name,
                    amount,
                    query_name,
                )

                await asyncio.sleep(amount)
            except (OSError, InternalServerError, ServiceUnavailable) as e:
                log.warning(
                    '[%s] Retrying "%s" due to: %s', attempt, query_name, str(e) or repr(e)
                )

                await asyncio.sleep(retry_delay)

        raise TimeoutError(f'Failed to invoke "{query_name}" after {retries} retries')

    def __str__(self) -> str:
        return f"Session(dc_id={self.dc_id}, test_mode={self.test_mode}, is_media={self.is_media}, is_cdn={self.is_cdn}, state={self._state.name})"
