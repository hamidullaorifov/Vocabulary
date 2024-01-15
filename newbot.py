import os
import sys
import django
import random
sys.dont_write_bytecode = True




os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Vocabulary.settings')
django.setup()

from telegram import Update,ReplyKeyboardRemove
from telegram.ext import Updater, Dispatcher, Filters, CallbackContext, \
    MessageHandler, CommandHandler, CallbackQueryHandler
from telegram import Bot
from datetime import date
from utils import text_to_dic
from handlers import *


from dotenv import load_dotenv
load_dotenv()


token = os.getenv('TOKEN')





updater = Updater(token=token)
# updater = Updater(token=token,request_kwargs={'connect_timeout': 120000})
dispatcher: Dispatcher = updater.dispatcher

bot = Bot(token=token)

FIND_WORD_STATE, FIND_MEANING_STATE,CREATE_DICT_STATE,TEST_STATE = range(4)







def stop_handler(update: Update, context: CallbackContext):
    update.message.reply_text('Good bye!', reply_markup=ReplyKeyboardRemove())

 

dispatcher.add_handler(CommandHandler('start',start_handler))
dispatcher.add_handler(CallbackQueryHandler(callback=new_dictionary_handler,pattern=r'^new_dictionary$'))
dispatcher.add_handler(CallbackQueryHandler(callback=find_word_handler,pattern=r'^find_word$'))
dispatcher.add_handler(CallbackQueryHandler(callback=find_meaning_handler,pattern=r'^find_meaning$'))
dispatcher.add_handler(CallbackQueryHandler(callback=choose_period_handler,pattern=r'period_\w+\b'))
dispatcher.add_handler(CallbackQueryHandler(callback=choose_category_list_handler,pattern=r'^choose_category\|'))
dispatcher.add_handler(CallbackQueryHandler(callback=choose_category_handler,pattern=r'category\|(\d+)'))
dispatcher.add_handler(CallbackQueryHandler(callback=quiz_callback_handler,pattern=r'^(no|yes|check)$'))
dispatcher.add_handler(CallbackQueryHandler(callback=back_to_menu,pattern=r'^back_to_menu$'))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command,callback=handle_dictionary_text))
dispatcher.add_handler(MessageHandler(Filters.document,callback=handle_dictionary_file))
dispatcher.add_handler(MessageHandler(Filters.regex(r'Back to menu$'),callback=back_to_menu),)


def all_handler(update:Update,context:CallbackContext):
    update.message.reply_text('bu hammasi')
    return 1


url='https://my-mbsaver-bot.herokuapp.com/'

updater.start_polling()

updater.idle()

