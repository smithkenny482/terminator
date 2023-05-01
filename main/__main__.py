import logging
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.error import TimedOut
from telegram.ext import CommandHandler, InlineQueryHandler, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ParseMode, ReplyKeyboardMarkup , ReplyKeyboardRemove
from telegram.ext import Updater, CallbackQueryHandler, CallbackContext , Filters, JobQueue , MessageHandler
import random
import json
import time
import asyncio
import os
import requests
from datetime import datetime
from telegram.ext import Handler
from telegram import Bot
import telegram
 
from datetime import datetime, timedelta
from telegram.ext import JobQueue

bot_token = '5602217970:AAFN0Sj8bakFutyYZ2__cnZX5lIy-lOiDpA'
 
updater = Updater(token=bot_token, use_context=True)
dispatcher = updater.dispatcher
 
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
 
logger = logging.getLogger()
 
updater.start_polling(drop_pending_updates = True)
 
group_user_ids = {}
job_queue = updater.job_queue
owners = [163494588,1729951756]
 
def filter_join_messages(update, context):
    message = update.message
    chat_id = message.chat_id
    new_members = message.new_chat_members
    left_member = message.left_chat_member
    current_time = datetime.now()
    print(group_user_ids)
    if new_members:
        the_id = 0
        user_ids = group_user_ids.get(chat_id, {}).get("user_ids", [])
        for member in new_members:
            user_id = member.id
            the_id += member.id
            user_ids.append(user_id)
        n = group_user_ids.get(chat_id, {}).get("n", 0)
        text = group_user_ids.get(chat_id, {}).get("text", "{user}\nhow are you doing")
        default_time = group_user_ids.get(chat_id, {}).get("default_time", 600)
        photo_link = group_user_ids.get(chat_id, {}).get("photo", None)
        ongoing = group_user_ids.get(chat_id, {}).get("ongoing", False)
        group_user_ids[chat_id] = {"user_ids": user_ids, "n": n, "text": text , 'default_time':default_time ,
                                   'last_join_time':current_time , 'photo':photo_link , 'ongoing': ongoing}
        message.delete()
 
        user_name = context.bot.get_chat_member(chat_id, the_id).user.first_name
        values = {
            "user": f'<a href="tg://user?id={the_id}">{user_name}</a>',
            "group": update.effective_chat.title
        }
        display_text = text.format_map(values)
        if ongoing:
            if group_user_ids[chat_id]['photo'] is None:
                context.bot.send_message(chat_id=chat_id, text=display_text,
                                 parse_mode=telegram.ParseMode.HTML)
 
            elif group_user_ids[chat_id]['photo'] is not None:
                context.bot.send_photo(chat_id = chat_id , caption = display_text , photo = group_user_ids[chat_id]['photo'] , parse_mode=telegram.ParseMode.HTML)
 
        job_queue.run_repeating(countdown, interval=10, first=0, context=chat_id)
 
    elif left_member:
        user_ids = group_user_ids.get(chat_id, {}).get("user_ids", [])
        user_id = left_member.id
        if user_id in user_ids:
            user_ids.remove(user_id)
        message.delete()
    else:
        user_ids = group_user_ids.get(chat_id, {}).get("user_ids", [])
        if user_ids:
            # the job is already started when the first user joined
            pass
        else:
            # no users in the group yet
            pass
 
def countdown(context):
    chat_id = context.job.context
    user_ids = group_user_ids.get(chat_id, {}).get("user_ids", [])
    last_join_time = group_user_ids.get(chat_id, {}).get("last_join_time", None)
    current_time = datetime.now()
    print(current_time)
    default_time = group_user_ids.get(chat_id, {}).get("default_time", 600)
    if not last_join_time:
        return
 
    if group_user_ids[chat_id]['ongoing'] == False:
        return
 
    delta_time = current_time - last_join_time
    if delta_time.seconds > default_time:
        text = group_user_ids.get(chat_id, {}).get("text", "how are you doing?")
        user_id = user_ids[group_user_ids.get(chat_id, {}).get("n", 0)]
        user_name = context.bot.get_chat_member(chat_id, user_id).user.first_name
 
        values = {
            "user": f'<a href="tg://user?id={user_id}">{user_name}</a>'
        }
        display_text = text.format_map(values)
 
        if group_user_ids[chat_id]['photo'] is None:
            context.bot.send_message(chat_id=chat_id, text=display_text,
                                     parse_mode=telegram.ParseMode.HTML)
 
        elif group_user_ids[chat_id]['photo'] is not None:
            context.bot.send_photo(chat_id=chat_id, caption=display_text, photo=group_user_ids[chat_id]['photo'],
                                   parse_mode=telegram.ParseMode.HTML)
 
        n = (group_user_ids.get(chat_id, {}).get("n", 0) + 1) % len(user_ids)
        group_user_ids[chat_id]["n"] = n
        group_user_ids[chat_id]["last_join_time"] = current_time
 
def change_default_time(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in owners:
        update.message.reply_text('Not authorised to use this command')
        return
 
    chat_id = update.message.chat_id
    args = context.args
    if not args:
        update.message.reply_text("Please provide a new default time value in seconds.")
        return
    try:
        new_time = int(args[0])
    except ValueError:
        update.message.reply_text("Invalid time value. Please provide an integer value in seconds.")
        return
    if chat_id not in group_user_ids:
        update.message.reply_text("This command can only be used in groups where the bot is present.")
        return
    group_info = group_user_ids[chat_id]
    group_info['default_time'] = new_time
    group_user_ids[chat_id] = group_info
    update.message.reply_text(f"Default time value for this group has been updated to {new_time} seconds.")
 
def change_text(update , context):
    user_id = update.effective_user.id
    if user_id not in owners:
        update.message.reply_text('Not authorised to use this command')
        return
 
    chat_id = update.message.chat_id
    args = context.args
    if not args:
        update.message.reply_text("Please provide a new text message.")
        return
 
    new_text = update.message.text[10:]
    if chat_id not in group_user_ids:
        update.message.reply_text("This command can only be used in groups where the bot is present.")
        return
 
    group_info = group_user_ids[chat_id]
    group_info['text'] = new_text
    group_user_ids[chat_id] = group_info
    update.message.reply_text(f"Default message for this group has been updated.")
 
def change_photo(update , context):
    user_id = update.effective_user.id
    if user_id not in owners:
        update.message.reply_text('Not authorised to use this command')
        return
 
    chat_id = update.message.chat_id
    args = context.args
    if not args:
        update.message.reply_text("Please provide link of photo")
        return
 
    new_photo = update.message.text[11:]
    if chat_id not in group_user_ids:
        update.message.reply_text("This command can only be used in groups where the bot is present.")
        return
 
    group_info = group_user_ids[chat_id]
    group_info['photo'] = new_photo
    group_user_ids[chat_id] = group_info
    update.message.reply_text(f"photo for this group has been updated.")
 
def run(update , context):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    if user_id not in owners:
        update.message.reply_text('Not authorised to use this command')
        return
 
    group_user_ids[chat_id]['ongoing'] = True
    update.message.reply_text('Activated')
 
def pause(update , context):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    if user_id not in owners:
        update.message.reply_text('Not authorised to use this command')
        return
 
    group_user_ids[chat_id]['ongoing'] = False
    update.message.reply_text('Paused')
 
def admin_list(update , context):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    if user_id != owners[0]:
        update.message.reply_text('Owner command 🔐 , you are not owner')
        return
 
    text = f'Owner : {owners[0]}\n\nAuthorised user list :\n'
    num = 0
    for i in owners:
        text+=f'{num+1}. {i}\n'
        num+=1
 
    update.message.reply_text(text)
 
def add_admin(update , context):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    if user_id != owners[0]:
        update.message.reply_text('Owner command 🔐 , you are not owner')
        return
 
    try:
        target_id = update.message.reply_to_message.from_user.id
        if target_id in owners:
            update.message.reply_text(f'{target_id} is already authorised')
            return
        elif target_id not in owners:
            owners.append(target_id)
            update.message.reply_text(f'{target_id} is now authorised user of bot')
            return
    except AttributeError:
        update.message.reply_text('Reply to the person you wish to transfer ownership')
 
def remove_admin(update , context):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    if user_id != owners[0]:
        update.message.reply_text('Owner command 🔐 , you are not owner')
        return
 
    try:
        target_id = update.message.reply_to_message.from_user.id
        if target_id == owners[0]:
            update.message.reply_text(f'You cannot remove yourself')
            return
 
        if target_id not in owners:
            update.message.reply_text(f'{target_id} is not in authorised user list')
 
        elif target_id in owners:
            owners.remove(target_id)
            update.message.reply_text(f'{target_id} is removed from authorised user of bot')
 
    except AttributeError:
        update.message.reply_text('Reply to the person you wish to transfer ownership')
 
def transfer_owner(update , context):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    if user_id != owners[0]:
        update.message.reply_text('Owner command 🔐 , you are not owner')
        return
 
    try:
        target_id = update.message.reply_to_message.from_user.id
        owners.append(user_id)
        owners.remove(target_id)
        owners[0] = target_id
        update.message.reply_text(f'Ownership has been passed onto user {target_id}')
 
    except AttributeError:
        update.message.reply_text('Reply to the person you wish to transfer ownership')
 
def status(update , context):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
 
    if user_id not in owners:
        update.message.reply_text('Not authorised to use this command')
        return
 
    timer = group_user_ids[chat_id]['default_time']
    default_text = group_user_ids[chat_id]['text']
    photo = group_user_ids[chat_id]['photo']
    ongoing = group_user_ids[chat_id]['ongoing']
    users = len(group_user_ids[chat_id]['user_ids'])
 
    text = '<b>📊 Status for this group</b>\n\n'
    text+=f'Default time : {timer} seconds\n'
    text+=f'Currently running : {ongoing}\n'
    text+=f'Photo used : {photo}\n'
    text+=f'User tracked by bot : {users}\n'
    text+=f'Text message : {default_text}\n'
 
    update.message.reply_text(text , parse_mode = ParseMode.HTML)
 
def test(update , context):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user_name = context.bot.get_chat_member(chat_id, user_id).user.first_name
    text= f'<a href="tg://user?id={user_id}">{user_name}</a>\n'
    text+=f"how are you doing?"
    update.message.reply_text(text, parse_mode=telegram.ParseMode.HTML)
 
message_handler = MessageHandler(Filters.all & Filters.chat_type.groups, filter_join_messages)
dispatcher.add_handler(CommandHandler("set_time", change_default_time))
dispatcher.add_handler(CommandHandler("set_text", change_text))
dispatcher.add_handler(CommandHandler("set_photo", change_photo))
dispatcher.add_handler(CommandHandler("status", status))
dispatcher.add_handler(CommandHandler("add_admin", add_admin))
dispatcher.add_handler(CommandHandler("remove_admin", remove_admin))
dispatcher.add_handler(CommandHandler("admin_list", admin_list))
dispatcher.add_handler(CommandHandler("transfer_owner", transfer_owner))
dispatcher.add_handler(CommandHandler("run", run))
dispatcher.add_handler(CommandHandler("pause", pause))
dispatcher.add_handler(CommandHandler("test", test))
