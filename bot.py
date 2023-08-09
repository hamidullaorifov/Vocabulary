import os
import sys
import django
import random
sys.dont_write_bytecode = True




os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Vocabulary.settings')
django.setup()

from telegram import ReplyMarkup, Update, ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton,ReplyKeyboardRemove
from telegram.ext import Updater, Dispatcher, Filters, CallbackContext, \
    MessageHandler, CommandHandler, CallbackQueryHandler,ConversationHandler
from telegram import Bot
from datetime import date
from utils import text_to_dic
from dictionary.models import Dictionary
from dotenv import load_dotenv
load_dotenv()


token = os.getenv('TOKEN')





updater = Updater(token=token)
# updater = Updater(token=token,request_kwargs={'connect_timeout': 120000})
dispatcher: Dispatcher = updater.dispatcher

bot = Bot(token=token)

MENU_STATE, QUIZ_STATE,NEW_DIC_STATE, TEST_STATE = range(4)


def menu_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton('Find meaning'),KeyboardButton('Find Word')],
        [KeyboardButton('New Dictionary')],
    ], resize_keyboard=True, one_time_keyboard=True)




def start_handler(update:Update,context:CallbackContext):
    update.message.reply_text('Hello,Choose menu!',reply_markup=menu_keyboard())
    return MENU_STATE

def stop_handler(update: Update, context: CallbackContext):
    update.message.reply_text('Good bye!', reply_markup=ReplyKeyboardRemove())

 

# def error(update:Update,context:CallbackContext):
#     print('Error occured')


def test_single_dic(update:Update,context:CallbackContext):
    dics = context.chat_data['dictionary']
    message = update.message or update.callback_query.message
    if dics:
        last = dics.pop()
        word = last[0]
        meaning= last[1]
        example = last[2]
        context.chat_data.update({
            'current_word':word,
            'current_word_meaning':meaning,
            'current_example':example,
            'dictionary':dics,
        })
        message.reply_text(text=word,reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='Check',callback_data=f'check'),]]))
        return TEST_STATE
    else:
        text = 'Unfound words:\n'
        
        unf_words = context.chat_data['unfound_words']
        for i,w in enumerate(unf_words,start=1):
            key = w[0]
            text+=f'{i}. {key} - {w[1]}\nExample: {w[2]}\n'
        message = update.message or update.callback_query.message
        message.reply_text(text=text)
        return back_to_menu(update,context)

def back_to_menu(update:Update,context:CallbackContext):
    message = update.message or update.callback_query.message
    message.reply_text('Choose menu!',reply_markup=menu_keyboard())
    return MENU_STATE
def test_all_dicts(update:Update,context:CallbackContext):
    operation = context.chat_data['operation']
    dics_list = Dictionary.objects.all().order_by("?")[:10]
    if operation == 'find_meaning':
        dics = [(d.word,d.meaning,d.example) for d in dics_list]
    else:
        dics = [(d.meaning,d.word,d.example) for d in dics_list]
    if dics:
        context.chat_data.update({
            'dictionary':dics,
            'unfound_words':[],
        })

        return test_single_dic(update,context)
    else:
        update.message.reply_text(text='There is no any dictionary.Create dictionary,please')
        return NEW_DIC_STATE
    



def find_meaning(update:Update,context:CallbackContext):
    context.chat_data.update({
        'operation':'find_meaning'
    })
    update.message.reply_text(text='Test type:( all, last_n, date_d/m/y or date_d.m.y)',reply_markup=ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton('Back to menu')]
    ],resize_keyboard=True,one_time_keyboard=True))
    return QUIZ_STATE
def find_word(update:Update,context:CallbackContext):
    context.chat_data.update({
        'operation':'find_word',
    })
    update.message.reply_text(text='Test type:( all, last_n, date_d/m/y or date_d.m.y)',reply_markup=ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton('Back to menu')]
    ],resize_keyboard=True,one_time_keyboard=True))
    return QUIZ_STATE
def new_dic(update:Update,context:CallbackContext):
    update.message.reply_text(text="Send text",reply_markup=ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton('Back to menu')]
    ],resize_keyboard=True,one_time_keyboard=True))
    return NEW_DIC_STATE
def create_dic(update:Update,context:CallbackContext):
    text = update.message.text
    dic,date_str = text_to_dic(text)
    if date_str is not None:
        d = date_str.split('.')
        created = date(year=int(d[2]),month=int(d[1]),day=int(d[0]))
    else:
        created = date.today()
    
    for d in dic:
        Dictionary.objects.get_or_create(word=d[0],meaning=d[1],example=d[2],created=created)
    # for d in uz_en:
    #     Dictionary.objects.get_or_create(lang='uz',word=d,translate=uz_en[d],created=created)
    update.message.reply_text(text='Successfully created',reply_markup=ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton('Back to menu')]
    ],resize_keyboard=True,one_time_keyboard=True))
    return NEW_DIC_STATE
def test_callback_handler(update:Update,context:CallbackContext):
    callback_data = update.callback_query.data
    if callback_data=='check':
        update.callback_query.message.reply_text(
            text=f"{context.chat_data['current_word_meaning']}\nExample: {context.chat_data['current_example']}",
            reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='❎',callback_data=f'no'),
            InlineKeyboardButton(text='✅',callback_data=f'yes')]]
        ))
        return TEST_STATE
    elif callback_data == 'no':
        unfound_words = context.chat_data['unfound_words']
        unfound_word = context.chat_data['current_word']
        unfound_word_meaning = context.chat_data['current_word_meaning']
        example = context.chat_data['current_example']
        unfound_words.append((unfound_word,unfound_word_meaning,example))
        context.chat_data.update({
            'unfound_words':unfound_words,
        })
        return test_single_dic(update,context)
    elif callback_data == 'yes':
        return test_single_dic(update,context)
        
def test_full_dicts(update:Update,context:CallbackContext):
    operation = context.chat_data['operation']
    dics_list = Dictionary.objects.all().order_by("?")
    if operation == 'find_meaning':
        dics = [(d.word,d.meaning,d.example) for d in dics_list]
    else:
        dics = [(d.meaning,d.word,d.example) for d in dics_list]
    if dics:
        context.chat_data.update({
            'dictionary':dics,
            'unfound_words':[],
        })

        return test_single_dic(update,context)
    else:
        update.message.reply_text(text='There is no any dictionary.Create dictionary,please')
        return NEW_DIC_STATE


def test_by_date(update:Update,context:CallbackContext):
    text = update.message.text
    sep = ''
    if text.find('/')>0:
        sep = '/'
    elif text.find('.')>0:
        sep = '.'
    date_str = text.split('_')[1]
    d = date_str.split(sep)
    created = date(year=int(d[2]),month=int(d[1]),day=int(d[0]))
    operation = context.chat_data['operation']
    dics_list = Dictionary.objects.filter(created=created)
    if operation == 'find_meaning':
        dics = [(d.word,d.meaning,d.example) for d in dics_list]
    else:
        dics = [(d.meaning,d.word,d.example) for d in dics_list]
    random.shuffle(dics)
    if dics:
        context.chat_data.update({
            'dictionary':dics,
            'unfound_words':[],
        })

        return test_single_dic(update,context)
    else:
        update.message.reply_text(text='There is no any dictionary.Create dictionary,please')
        return NEW_DIC_STATE
def test_by_before_date(update:Update,context:CallbackContext):
    text = update.message.text
    sep = ''
    if text.find('/')>0:
        sep = '/'
    elif text.find('.')>0:
        sep = '.'
    date_str = text.split('_')[1]
    d = date_str.split(sep)
    created = date(year=int(d[2]),month=int(d[1]),day=int(d[0]))
    operation = context.chat_data['operation']
    dics_list = Dictionary.objects.filter(created__lt=created)
    if operation == 'find_meaning':
        dics = [(d.word,d.meaning,d.example) for d in dics_list]
    else:
        dics = [(d.meaning,d.word,d.example) for d in dics_list]
    random.shuffle(dics)
    dics = dics[:20]
    if dics:
        context.chat_data.update({
            'dictionary':dics,
            'unfound_words':[],
        })

        return test_single_dic(update,context)
    else:
        update.message.reply_text(text='There is no any dictionary.Create dictionary,please')
        return NEW_DIC_STATE


def test_last_n(update:Update,context:CallbackContext):
    text = update.message.text
    operation = context.chat_data['operation']
    count = int(text.split('_')[1])
    dics_list = Dictionary.objects.all()[:count]
    if operation == 'find_meaning':
        dics = [(d.word,d.meaning,d.example) for d in dics_list]
    else:
        dics = [(d.meaning,d.word,d.example) for d in dics_list]
    random.shuffle(dics)
    dics = dics[:10]
    if dics:
        context.chat_data.update({
            'dictionary':dics,
            'unfound_words':[],
        })

        return test_single_dic(update,context)
    else:
        update.message.reply_text(text='There is no any dictionary.Create dictionary,please')
        return NEW_DIC_STATE
def test_last_n_m(update:Update,context:CallbackContext):
    text = update.message.text
    operation = context.chat_data['operation']
    word_count = int(text.split('_')[1])
    test_count = int(text.split('_')[2])
    dics_list = Dictionary.objects.all()[:word_count]
    if operation == 'find_meaning':
        dics = [(d.word,d.meaning,d.example) for d in dics_list]
    else:
        dics = [(d.meaning,d.word,d.example) for d in dics_list]
    random.shuffle(dics)
    dics = dics[:test_count]
    if dics:
        context.chat_data.update({
            'dictionary':dics,
            'unfound_words':[],
        })

        return test_single_dic(update,context)
    else:
        update.message.reply_text(text='There is no any dictionary.Create dictionary,please')
        return NEW_DIC_STATE

dispatcher.add_handler(ConversationHandler(
    entry_points=[MessageHandler(Filters.all,start_handler),],
    states={  
        MENU_STATE:
        [
            MessageHandler(Filters.regex(r'Back to menu$'),callback=back_to_menu),
            MessageHandler(Filters.regex(r'Find meaning$'),callback=find_meaning),
            MessageHandler(Filters.regex(r'Find Word$'),callback=find_word),
            MessageHandler(Filters.regex(r'New Dictionary$'),callback=new_dic),
        ],
        QUIZ_STATE:
        [
           MessageHandler(Filters.regex(r'Back to menu$'),callback=back_to_menu), 
           MessageHandler(Filters.regex(r'full$'),callback=test_full_dicts), 
           MessageHandler(Filters.regex(r'all$'),callback=test_all_dicts), 
           MessageHandler(Filters.regex(r'^date_[0-9]{2}/[0-9]{2}/[0-9]{4}$'),callback=test_by_date),
           MessageHandler(Filters.regex(r'^date_[0-9]{1}/[0-9]{2}/[0-9]{4}$'),callback=test_by_date),
           MessageHandler(Filters.regex(r'^date_[0-9]{2}.[0-9]{2}.[0-9]{4}$'),callback=test_by_date),
           MessageHandler(Filters.regex(r'^date_[0-9]{1}.[0-9]{2}.[0-9]{4}$'),callback=test_by_date),
           MessageHandler(Filters.regex(r'^beforedate_[0-9]{2}/[0-9]{2}/[0-9]{4}$'),callback=test_by_before_date),
           MessageHandler(Filters.regex(r'^beforedate_[0-9]{1}/[0-9]{2}/[0-9]{4}$'),callback=test_by_before_date),
           MessageHandler(Filters.regex(r'^beforedate_[0-9]{2}.[0-9]{2}.[0-9]{4}$'),callback=test_by_before_date),
           MessageHandler(Filters.regex(r'^beforedate_[0-9]{1}.[0-9]{2}.[0-9]{4}$'),callback=test_by_before_date),
           MessageHandler(Filters.regex(r'last_[0-9]'),callback=test_last_n),
           MessageHandler(Filters.regex(r'last_[0-9]_[0-9]'),callback=test_last_n_m),
           CallbackQueryHandler(callback=test_callback_handler),
        ],
        TEST_STATE:
        [   
            MessageHandler(Filters.regex(r'Back to menu$'),callback=back_to_menu),
            CallbackQueryHandler(callback=test_callback_handler),
        ],
        NEW_DIC_STATE:
        [   
            MessageHandler(Filters.regex(r'Back to menu$'),callback=back_to_menu),
            MessageHandler(filters=Filters.text,callback=create_dic)
        ],
        
    },
    fallbacks=[CommandHandler('stop', stop_handler)]
))
    
    

dispatcher.add_handler(MessageHandler(Filters.regex(r'Back to menu$'),callback=back_to_menu),)


def all_handler(update:Update,context:CallbackContext):
    update.message.reply_text('bu hammasi')
    return MENU_STATE

dispatcher.add_handler(CommandHandler('start',start_handler))
dispatcher.add_handler(MessageHandler(Filters.all,callback=all_handler))
# dispatcher.add_error_handler(callback=error)

url='https://my-mbsaver-bot.herokuapp.com/'

updater.start_polling()
# updater.start_webhook(listen="0.0.0.0",
#                         port=int(os.environ.get('PORT', 8443)),
#                         url_path=token,
#                         webhook_url=url + token)

updater.idle()

