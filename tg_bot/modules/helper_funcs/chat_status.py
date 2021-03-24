from functools import wraps
from typing import Optional

from telegram import User, Chat, ChatMember, Update, Bot

from tg_bot import DEL_CMDS, SUDO_USERS, WHITELIST_USERS


_TELE_GRAM_ID_S = [777000, 7351948, 861055237]


def can_delete(chat: Chat, bot_id: int) -> bool:
    return chat.get_member(bot_id).can_delete_messages


def is_user_ban_protected(chat: Chat, user_id: int, member: ChatMember = None) -> bool:
    if user_id in _TELE_GRAM_ID_S:
        return True

    if chat.type == 'private' \
            or user_id in SUDO_USERS \
            or user_id in WHITELIST_USERS \
            or chat.all_members_are_administrators:
        return True

    if not member:
        member = chat.get_member(user_id)
    return member.status in ('administrator', 'creator')


def is_user_admin(chat: Chat, user_id: int, member: ChatMember = None) -> bool:
    if user_id in _TELE_GRAM_ID_S:
        return True

    if chat.type == 'private' \
            or user_id in SUDO_USERS \
            or chat.all_members_are_administrators:
        return True

    if not member:
        member = chat.get_member(user_id)
    return member.status in ('administrator', 'creator')


def is_bot_admin(chat: Chat, bot_id: int, bot_member: ChatMember = None) -> bool:
    if chat.type == 'private' \
            or chat.all_members_are_administrators:
        return True

    if not bot_member:
        bot_member = chat.get_member(bot_id)
    return bot_member.status in ('administrator', 'creator')


def is_user_in_chat(chat: Chat, user_id: int) -> bool:
    member = chat.get_member(user_id)
    return member.status not in ('left', 'kicked')


def bot_can_delete(func):
    @wraps(func)
    def delete_rights(bot: Bot, update: Update, *args, **kwargs):
        if can_delete(update.effective_chat, bot.id):
            return func(bot, update, *args, **kwargs)
        else:
            update.effective_message.reply_text("എനിക്ക് ഇവിടെ സന്ദേശങ്ങൾ ഇല്ലാതാക്കാൻ കഴിയില്ല! "
                                                "ഞാൻ അഡ്മിൻ ആണെന്ന് ഉറപ്പാക്കുക, മറ്റ് ഉപയോക്താവിന്റെ സന്ദേശങ്ങൾ ഇല്ലാതാക്കാൻ എനിക്ക് അനുമതിയുണ്ടെന്ന് ഉറപ്പാക്കുക.")

    return delete_rights


def can_pin(func):
    @wraps(func)
    def pin_rights(bot: Bot, update: Update, *args, **kwargs):
        if update.effective_chat.get_member(bot.id).can_pin_messages:
            return func(bot, update, *args, **kwargs)
        else:
            update.effective_message.reply_text("എനിക്ക് സന്ദേശങ്ങൾ ഇവിടെ പിൻ ചെയ്യാനാവില്ല! "
                                                "ഞാൻ അഡ്മിൻ ആണെന്ന് ഉറപ്പാക്കുക, സന്ദേശങ്ങൾ പിൻ ചെയ്യാനുള്ള അനുമതി എനിക്ക് ഉണ്ടെന്ന് ഉറപ്പാക്കുക.")

    return pin_rights


def can_promote(func):
    @wraps(func)
    def promote_rights(bot: Bot, update: Update, *args, **kwargs):
        if update.effective_chat.get_member(bot.id).can_promote_members:
            return func(bot, update, *args, **kwargs)
        else:
            update.effective_message.reply_text("എനിക്ക് ആളുകളെ പ്രോത്സാഹിപ്പിക്കാനോ / പ്രകടിപ്പിക്കാനോ കഴിയില്ല! "
                                                "ഞാൻ അഡ്മിനാണെന്നും പുതിയ അഡ്മിനുകളേ എനിക്ക് നിയമിക്കാൻ കഴിയുമെന്നും ഉറപ്പാക്കുക.")

    return promote_rights


def can_restrict(func):
    @wraps(func)
    def promote_rights(bot: Bot, update: Update, *args, **kwargs):
        if update.effective_chat.get_member(bot.id).can_restrict_members:
            return func(bot, update, *args, **kwargs)
        else:
            update.effective_message.reply_text("എനിക്ക് ഇവിടെ ആളുകളെ നിയന്ത്രിക്കാനാവില്ല! "
                                                "ഞാൻ അഡ്മിനാണെന്നും പുതിയ അഡ്മിനുകളേ എനിക്ക് നിയമിക്കാൻ കഴിയുമെന്നും ഉറപ്പാക്കുക.")

    return promote_rights


def bot_admin(func):
    @wraps(func)
    def is_admin(bot: Bot, update: Update, *args, **kwargs):
        if is_bot_admin(update.effective_chat, bot.id):
            return func(bot, update, *args, **kwargs)
        else:
            update.effective_message.reply_text("ഞാൻ അഡ്മിനല്ല!")

    return is_admin


def user_admin(func):
    @wraps(func)
    def is_admin(bot: Bot, update: Update, *args, **kwargs):
        user = update.effective_user  # type: Optional[User]
        if user and is_user_admin(update.effective_chat, user.id):
            return func(bot, update, *args, **kwargs)

        elif not user:
            pass

        elif DEL_CMDS and " " not in update.effective_message.text:
            update.effective_message.delete()

        else:
            update.effective_message.reply_text("ഏതാണ് ഈ മനുഷ്യൻ ഞാൻ എന്ത് ചെയ്യണം എന്ന് പറയുന്നത്?")

    return is_admin


def user_admin_no_reply(func):
    @wraps(func)
    def is_admin(bot: Bot, update: Update, *args, **kwargs):
        user = update.effective_user  # type: Optional[User]
        if user and is_user_admin(update.effective_chat, user.id):
            return func(bot, update, *args, **kwargs)

        elif not user:
            pass

        elif DEL_CMDS and " " not in update.effective_message.text:
            update.effective_message.delete()

    return is_admin


def user_not_admin(func):
    @wraps(func)
    def is_not_admin(bot: Bot, update: Update, *args, **kwargs):
        user = update.effective_user  # type: Optional[User]
        if user and not is_user_admin(update.effective_chat, user.id):
            return func(bot, update, *args, **kwargs)

    return is_not_admin
