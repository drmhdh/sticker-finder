"""Session helper functions."""
import traceback
from functools import wraps
from telegram.error import (
    TelegramError,
    ChatMigrated,
    Unauthorized,
)

from stickerfinder.config import config
from stickerfinder.db import get_session
from stickerfinder.sentry import sentry
from stickerfinder.models import Chat, User
from stickerfinder.helper import error_text
from stickerfinder.helper.telegram import call_tg_func


def job_session_wrapper(check_ban=False, admin_only=False):
    """Create a session, handle permissions and exceptions for jobs."""
    def real_decorator(func):
        """Parametrized decorator closure."""
        @wraps(func)
        def wrapper(context):
            session = get_session()
            try:
                func(context, session)

                session.commit()
            finally:
                session.close()
        return wrapper

    return real_decorator


def hidden_session_wrapper(check_ban=False, admin_only=False):
    """Create a session, handle permissions and exceptions."""
    def real_decorator(func):
        """Parametrized decorator closure."""
        @wraps(func)
        def wrapper(update, context):
            session = get_session()
            try:
                user = get_user(session, update)
                if not is_allowed(user, update, admin_only=admin_only, check_ban=check_ban):
                    return

                func(context.bot, update, session, user)

                session.commit()
            # Raise all telegram errors and let the generic error_callback handle it
            finally:
                session.close()
        return wrapper

    return real_decorator


def session_wrapper(send_message=True, check_ban=False,
                    admin_only=False, private=False, allow_edit=False):
    """Create a session, handle permissions, handle exceptions and prepare some entities."""
    def real_decorator(func):
        """Parametrized decorator closure."""
        @wraps(func)
        def wrapper(update, context):
            session = get_session()
            try:
                user = get_user(session, update)
                if not is_allowed(user, update, admin_only=admin_only, check_ban=check_ban):
                    return

                if hasattr(update, 'message') and update.message:
                    message = update.message
                elif hasattr(update, 'edited_message') and update.edited_message:
                    message = update.edited_message

                chat_id = message.chat_id
                chat_type = message.chat.type
                chat = Chat.get_or_create(session, chat_id, chat_type)

                if not is_allowed(user, update, chat=chat, private=private):
                    return

                response = func(context.bot, update, session, chat, user)

                session.commit()
                # Respond to user
                if hasattr(update, 'message') and response is not None:
                    call_tg_func(message.chat, 'send_message', args=[response])

            # A user banned the bot
            except Unauthorized:
                session.delete(chat)

            # A group chat has been converted to a super group.
            except ChatMigrated:
                session.delete(chat)

            # Raise all telegram errors and let the generic error_callback handle it
            except TelegramError as e:
                raise e

            except BaseException as e:
                if send_message:
                    session.close()
                    call_tg_func(message.chat, 'send_message',
                                 args=[error_text])
                raise e
            finally:
                session.close()

        return wrapper

    return real_decorator


def get_user(session, update):
    """Get the user from the update."""
    user = None
    # Check user permissions
    if hasattr(update, 'message') and update.message:
        user = User.get_or_create(session, update.message.from_user)
    if hasattr(update, 'edited_message') and update.edited_message:
        user = User.get_or_create(session, update.edited_message.from_user)
    elif hasattr(update, 'inline_query') and update.inline_query:
        user = User.get_or_create(session, update.inline_query.from_user)
    elif hasattr(update, 'callback_query') and update.callback_query:
        user = User.get_or_create(session, update.callback_query.from_user)

    return user


def is_allowed(user, update, chat=None, admin_only=False,
               check_ban=False, private=False):
    """Check whether the user is allowed to access this endpoint."""
    if private and chat.type != 'private':
        call_tg_func(update.message.chat, 'send_message',
                     ['Please do this in a direct conversation with me.'])
        return False

    # Check if the user has been banned.
    if check_ban and user and user.banned:
        call_tg_func(update.message.chat, 'send_message',
                     ['You have been banned.'])
        return False

    # Check for admin permissions.
    if admin_only and user and not user.admin \
            and user.username != config.ADMIN.lower():
        call_tg_func(update.message.chat, 'send_message',
                     ['You are not authorized for this command.'])
        return False

    return True
