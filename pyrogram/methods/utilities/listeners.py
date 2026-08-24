import asyncio
from inspect import iscoroutinefunction
from typing import Callable, List, Optional, Union

import pyrogram
from pyrogram.errors import ListenerStopped, ListenerTimeout
from pyrogram.filters import Filter
from pyrogram.types import Identifier, Listener, ListenerTypes


class Listeners:
    async def listen(
        self: "pyrogram.Client",
        filters: Optional[Filter] = None,
        listener_type: ListenerTypes = ListenerTypes.MESSAGE,
        timeout: Optional[int] = None,
        unallowed_click_alert: Union[bool, str] = True,
        chat_id: Optional[Union[Union[int, str], List[Union[int, str]]]] = None,
        user_id: Optional[Union[Union[int, str], List[Union[int, str]]]] = None,
        message_id: Optional[Union[int, List[int]]] = None,
        inline_message_id: Optional[Union[str, List[str]]] = None,
    ):
        pattern = Identifier(
            from_user_id=user_id,
            chat_id=chat_id,
            message_id=message_id,
            inline_message_id=inline_message_id,
        )

        loop = self.loop or asyncio.get_event_loop()
        future = loop.create_future()

        listener = Listener(
            future=future,
            filters=filters,
            unallowed_click_alert=unallowed_click_alert,
            identifier=pattern,
            listener_type=listener_type,
        )

        future.add_done_callback(lambda _future: self.remove_listener(listener))

        self.listeners[listener_type].append(listener)

        try:
            return await asyncio.wait_for(future, timeout)
        except asyncio.TimeoutError:
            raise ListenerTimeout(timeout)

    async def ask(
        self: "pyrogram.Client",
        chat_id: Union[Union[int, str], List[Union[int, str]]],
        text: str,
        filters: Optional[Filter] = None,
        listener_type: ListenerTypes = ListenerTypes.MESSAGE,
        timeout: Optional[int] = None,
        unallowed_click_alert: Union[bool, str] = True,
        user_id: Optional[Union[Union[int, str], List[Union[int, str]]]] = None,
        message_id: Optional[Union[int, List[int]]] = None,
        inline_message_id: Optional[Union[str, List[str]]] = None,
        *args,
        **kwargs,
    ):
        sent_message = None
        if text.strip() != "":
            chat_to_ask = chat_id[0] if isinstance(chat_id, list) else chat_id
            sent_message = await self.send_message(chat_to_ask, text, *args, **kwargs)

        response = await self.listen(
            filters=filters,
            listener_type=listener_type,
            timeout=timeout,
            unallowed_click_alert=unallowed_click_alert,
            chat_id=chat_id,
            user_id=user_id,
            message_id=message_id,
            inline_message_id=inline_message_id,
        )
        if response:
            response.sent_message = sent_message

        return response

    def remove_listener(self: "pyrogram.Client", listener: Listener):
        try:
            self.listeners[listener.listener_type].remove(listener)
        except (KeyError, ValueError):
            pass

    def get_listener_matching_with_data(
        self: "pyrogram.Client", data: Identifier, listener_type: ListenerTypes
    ) -> Optional[Listener]:
        matching = []
        for listener in self.listeners[listener_type]:
            if listener.identifier.matches(data):
                matching.append(listener)

        def count_populated_attributes(listener_item: Listener):
            return listener_item.identifier.count_populated()

        return max(matching, key=count_populated_attributes, default=None)

    def get_listener_matching_with_identifier_pattern(
        self: "pyrogram.Client", pattern: Identifier, listener_type: ListenerTypes
    ) -> Optional[Listener]:
        matching = []
        for listener in self.listeners[listener_type]:
            if pattern.matches(listener.identifier):
                matching.append(listener)

        def count_populated_attributes(listener_item: Listener):
            return listener_item.identifier.count_populated()

        return max(matching, key=count_populated_attributes, default=None)

    def get_many_listeners_matching_with_data(
        self: "pyrogram.Client",
        data: Identifier,
        listener_type: ListenerTypes,
    ) -> List[Listener]:
        listeners = []
        for listener in self.listeners[listener_type]:
            if listener.identifier.matches(data):
                listeners.append(listener)
        return listeners

    def get_many_listeners_matching_with_identifier_pattern(
        self: "pyrogram.Client",
        pattern: Identifier,
        listener_type: ListenerTypes,
    ) -> List[Listener]:
        listeners = []
        for listener in self.listeners[listener_type]:
            if pattern.matches(listener.identifier):
                listeners.append(listener)
        return listeners

    async def stop_listening(
        self: "pyrogram.Client",
        listener_type: ListenerTypes = ListenerTypes.MESSAGE,
        chat_id: Optional[Union[Union[int, str], List[Union[int, str]]]] = None,
        user_id: Optional[Union[Union[int, str], List[Union[int, str]]]] = None,
        message_id: Optional[Union[int, List[int]]] = None,
        inline_message_id: Optional[Union[str, List[str]]] = None,
    ):
        pattern = Identifier(
            from_user_id=user_id,
            chat_id=chat_id,
            message_id=message_id,
            inline_message_id=inline_message_id,
        )
        listeners = self.get_many_listeners_matching_with_identifier_pattern(pattern, listener_type)

        for listener in listeners:
            await self.stop_listener(listener)

    async def stop_listener(self: "pyrogram.Client", listener: Listener):
        self.remove_listener(listener)

        if listener.future and not listener.future.done():
            listener.future.set_exception(ListenerStopped())

    def register_next_step_handler(
        self: "pyrogram.Client",
        callback: Callable,
        filters: Optional[Filter] = None,
        listener_type: ListenerTypes = ListenerTypes.MESSAGE,
        unallowed_click_alert: Union[bool, str] = True,
        chat_id: Optional[Union[Union[int, str], List[Union[int, str]]]] = None,
        user_id: Optional[Union[Union[int, str], List[Union[int, str]]]] = None,
        message_id: Optional[Union[int, List[int]]] = None,
        inline_message_id: Optional[Union[str, List[str]]] = None,
    ):
        pattern = Identifier(
            from_user_id=user_id,
            chat_id=chat_id,
            message_id=message_id,
            inline_message_id=inline_message_id,
        )

        listener = Listener(
            callback=callback,
            filters=filters,
            unallowed_click_alert=unallowed_click_alert,
            identifier=pattern,
            listener_type=listener_type,
        )

        self.listeners[listener_type].append(listener)
