import logging
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import CommandHandler, InlineQueryHandler, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ParseMode
from telegram.ext import Updater, CallbackQueryHandler, CallbackContext , Filters
import datetime
import random
 
bot_token = '5602217970:AAFN0Sj8bakFutyYZ2__cnZX5lIy-lOiDpA'
 
updater = Updater(token=bot_token, use_context=True)
dispatcher = updater.dispatcher
 
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
 
logger = logging.getLogger()
 
updater.start_polling(drop_pending_updates = True)
