import logging
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import CommandHandler, InlineQueryHandler, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ParseMode
from telegram.ext import Updater, CallbackQueryHandler, CallbackContext , Filters
import datetime
import random
 
bot_token = '5602217970:AAGMsH9BVKO9cF_7dyXHsTx3KTID6AD-0N0'
 
updater = Updater(token=bot_token, use_context=True)
dispatcher = updater.dispatcher
 
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
 
logger = logging.getLogger()
 
updater.start_polling(drop_pending_updates = True)
