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

from .accept_terms_of_service import AcceptTermsOfService
from .change_phone_number import ChangePhoneNumber
from .check_password import CheckPassword
from .connect import Connect
from .disconnect import Disconnect
from .get_active_sessions import GetActiveSessions
from .get_password_hint import GetPasswordHint
from .initialize import Initialize
from .log_out import LogOut
from .recover_password import RecoverPassword
from .resend_phone_number_code import ResendPhoneNumberCode
from .reset_session import ResetSession
from .reset_sessions import ResetSessions
from .send_phone_number_code import SendPhoneNumberCode
from .send_recovery_code import SendRecoveryCode
from .sign_in import SignIn
from .sign_in_bot import SignInBot
from .sign_up import SignUp
from .terminate import Terminate


class Auth(
    AcceptTermsOfService,
    ChangePhoneNumber,
    CheckPassword,
    Connect,
    Disconnect,
    GetActiveSessions,
    GetPasswordHint,
    Initialize,
    LogOut,
    RecoverPassword,
    ResendPhoneNumberCode,
    ResetSession,
    ResetSessions,
    SendPhoneNumberCode,
    SendRecoveryCode,
    SignIn,
    SignInBot,
    SignUp,
    Terminate
):
    pass
