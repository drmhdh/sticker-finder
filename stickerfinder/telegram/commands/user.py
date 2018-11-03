"""User management related commands."""
from stickerfinder.helper.keyboard import main_keyboard, admin_keyboard, get_language_keyboard
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.session import session_wrapper
from stickerfinder.models import User, Language, Task


@session_wrapper(admin_only=True)
def ban_user(bot, update, session, chat, user):
    """Send a help text."""
    name_to_ban = update.message.text.split(' ', 1)[1].lower()

    user_to_ban = session.query(User) \
        .filter(User.username == name_to_ban) \
        .one_or_none()

    if user_to_ban is None:
        user_to_ban = session.query(User) \
            .filter(User.id == name_to_ban) \
            .one_or_none()

    if user_to_ban:
        user_to_ban.banned = True
        return f'User {name_to_ban} banned'
    else:
        return 'Unknown username'


@session_wrapper(admin_only=True)
def unban_user(bot, update, session, chat, user):
    """Send a help text."""
    name_to_unban = update.message.text.split(' ', 1)[1].lower()

    user_to_unban = session.query(User) \
        .filter(User.username == name_to_unban) \
        .one_or_none()

    if user_to_unban is None:
        user_to_unban = session.query(User) \
            .filter(User.id == name_to_unban) \
            .one_or_none()

    if user_to_unban:
        user_to_unban.banned = False
        return f'User {name_to_unban} unbanned'
    else:
        return 'Unknown username'


@session_wrapper()
def cancel(bot, update, session, chat, user):
    """Send a help text."""
    chat.cancel()

    keyboard = admin_keyboard if chat.is_maintenance else main_keyboard
    call_tg_func(update.message.chat, 'send_message', ['All running commands are canceled'],
                 {'reply_markup': keyboard})


@session_wrapper()
def choosing_language(bot, update, session, chat, user):
    """Select a language for the user."""
    chat.choosing_language = True
    languages = session.query(Language).all()
    keyboard = get_language_keyboard(languages)
    call_tg_func(update.message.chat, 'send_message', ['Choose your language'],
                 {'reply_markup': keyboard})


@session_wrapper()
def new_language(bot, update, session, chat, user):
    """Send a help text."""
    language = update.message.text.split(' ', 1)[1].lower().strip()

    exists = session.query(Language).get(language)

    if exists is not None:
        return "Language already exists"

    task = Task(Task.NEW_LANGUAGE, user=user)
    task.message = language
    session.add(task)
    session.commit()

    return "Your language is proposed, it'll be added soon."
