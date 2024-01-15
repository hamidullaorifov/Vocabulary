import os
import sys
import django
sys.dont_write_bytecode = True




os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Vocabulary.settings')
django.setup()


from telegram.ext import CallbackContext,ConversationHandler,MessageFilter,MessageHandler,Filters,CommandHandler,CallbackQueryHandler
from telegram import  Update,InlineKeyboardMarkup, InlineKeyboardButton
from keyboard import menu_keyboard,periods_keyboard,back_to_menu_keyboard
from datetime import date,timedelta
from utils import text_to_dic,get_dictionary_from_xlsx
from dictionary.models import Dictionary,Category


FIND_WORD_STATE, FIND_MEANING_STATE,CREATE_DICT_STATE,TEST_STATE = range(4)

def start_handler(update:Update,context:CallbackContext):
    
    context.chat_data.clear()
    update.message.reply_text('Hello,Choose menu!',reply_markup=menu_keyboard())

    

def back_to_menu(update:Update,context:CallbackContext):
    context.chat_data.clear()
    message = update.message or update.callback_query.message
    message.reply_text('Choose menu!',reply_markup=menu_keyboard())
    

def filter_dictionaries(chat_id,period):
    user_dics = Dictionary.objects.filter(chat_id=chat_id)
    if period == 'all':
        dictionaries = user_dics.order_by("?")[:100]
    elif period == 'random20':
        dictionaries = user_dics.order_by("?")[:20]
    elif period == 'lastday':
        last_dict = user_dics.order_by('-created').first()
        if last_dict:
            dictionaries = user_dics.filter(created=last_dict.created)
        else:
            dictionaries=[]
    elif period == 'last3days':
        last_dict = user_dics.order_by('-created').first()
        if last_dict:
            dictionaries = user_dics.filter(created__gte=last_dict.created-timedelta(days=3))
        else:
            dictionaries=[]
    elif period == 'lastweek':
        last_dict = user_dics.order_by('-created').first()
        if last_dict:
            dictionaries = user_dics.filter(created__gte=last_dict.created-timedelta(days=7))
        else:
            dictionaries=[]
    else:
        dictionaries = []
    return dictionaries


def choose_category_handler(update:Update,context:CallbackContext):
    print('Category chose',update.callback_query.data)
    _,category_id = update.callback_query.data.split('|')
    category = Category.objects.get(pk=category_id)
    dictionaries = category.dictionary_set.all()
    set_context_dictionary(dictionaries,context)
    return quiz(update,context)


def choose_category_list_handler(update:Update,context:CallbackContext):
    last = int(update.callback_query.data.split('|')[1])
    all_categories = Category.objects.all()
    count = all_categories.count()
    categories = all_categories
    if count>last:
        categories = all_categories[last:min(last+10,count)]

    inline_keyboard = [
        [InlineKeyboardButton(text=category.title,callback_data=f'category|{category.pk}')]
        for category in categories
    ]
    if count > last+10:
        inline_keyboard.append(
            [InlineKeyboardButton(text='>>>',callback_data=f'choose_category|{last+10}')]
        )
    if 10 < last:
        inline_keyboard.append(
            [InlineKeyboardButton(text='<<<',callback_data=f'choose_category|{last-10}')]
        )
    update.callback_query.message.reply_text(text="Choose category",reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_keyboard))

def set_context_dictionary(dictionaries,context):
    state = context.chat_data.get('state','find_word')
    dics = []
    if state == 'find_meaning':
        dics = [
            {
                'word':d.word,
                'meaning':d.meaning,
                'example':d.example
            } for d in dictionaries
        ]   
    elif state == 'find_word':
        dics = [
            {
                'word':d.meaning,
                'meaning':d.word,
                'example':d.example
            } for d in dictionaries
        ]
    context.chat_data['dictionary'] = dics


def choose_period_handler(update:Update,context:CallbackContext):
    _,period = update.callback_query.data.split('_')
    chat_id = update.callback_query.message.chat_id
    
    dictionaries = filter_dictionaries(chat_id=chat_id,period=period)
    set_context_dictionary(dictionaries,context)
    return quiz(update,context)

def find_word_handler(update:Update,context:CallbackContext):
    context.chat_data['state'] = 'find_word'
    update.callback_query.message.reply_text(text="Choose period",reply_markup=periods_keyboard())
    return FIND_WORD_STATE
def find_meaning_handler(update:Update,context:CallbackContext):
    context.chat_data['state'] = 'find_meaning'
    update.callback_query.message.reply_text(text="Choose period",reply_markup=periods_keyboard())
    return FIND_MEANING_STATE

def quiz(update:Update,context:CallbackContext):
    dics = context.chat_data['dictionary']
    message = update.message or update.callback_query.message
    if dics:
        last = dics.pop()
        word = last['word']
        meaning= last['meaning']
        example = last['example']
        context.chat_data.update({
            'current_word':word,
            'current_word_meaning':meaning,
            'current_example':example,
            'dictionary':dics,
        })
        message.reply_text(text=word,reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='Check',callback_data=f'check'),]]))
    else:
        text = '*Unfound words:*\n'
        
        unf_words = context.chat_data.get('unfound_words',[])
        for i,w in enumerate(unf_words,start=1):
            key = w[0]
            text+=f'{i}. {key} - {w[1]}\nExample: {w[2]}\n'
        message = update.message or update.callback_query.message
        message.reply_text(text=text,reply_markup=back_to_menu_keyboard())
    

def quiz_callback_handler(update:Update,context:CallbackContext):
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
        unfound_words = context.chat_data.get('unfound_words',[])
        unfound_word = context.chat_data['current_word']
        unfound_word_meaning = context.chat_data['current_word_meaning']
        example = context.chat_data['current_example']
        unfound_words.append((unfound_word,unfound_word_meaning,example))
        context.chat_data.update({
            'unfound_words':unfound_words,
        })
        return quiz(update,context)
    elif callback_data == 'yes':
        return quiz(update,context)

def new_dictionary_handler(update: Update,context:CallbackContext):
    context.chat_data['state'] = 'new_dictionary'
    update.callback_query.message.reply_text("Send text or excel file",reply_markup=back_to_menu_keyboard())
    return CREATE_DICT_STATE
    
def handle_dictionary_text(update: Update,context:CallbackContext):
    print("TEXT")
    chat_id = update.message.chat_id
    text = update.message.text
    dic,date_str = text_to_dic(text)
    if date_str is not None:
        d = date_str.split('.')
        created = date(year=int(d[2]),month=int(d[1]),day=int(d[0]))
    else:
        created = date.today()
    
    for d in dic:
        Dictionary.objects.get_or_create(word=d[0],meaning=d[1],example=d[2],created=created,chat_id=chat_id)
    update.message.reply_text(text='Successfully created',reply_markup=back_to_menu_keyboard())
    return CREATE_DICT_STATE


def handle_dictionary_file(update: Update,context:CallbackContext):
    chat_id = update.message.chat_id
    try:
        document = update.message.document
        if document:
            print("TYPE : ",update.message.document.mime_type)
            file = document.get_file()
            dics = get_dictionary_from_xlsx(file.file_path)
            date_str = document.file_name
            print("DATE",date_str)
            if date_str is not None:
                try:
                    d = date_str.split('.')
                    created = date(year=int(d[2]),month=int(d[1]),day=int(d[0]))
                except:
                    created = date.today()
            else:
                created = date.today()
    
            for d in dics:
                Dictionary.objects.get_or_create(word=d[0],meaning=d[1],example=d[2],created=created,chat_id=chat_id)
            update.message.reply_text(text='Successfully created',reply_markup=back_to_menu_keyboard())
    except Exception as e:
        update.message.reply_text(e,reply_markup=back_to_menu_keyboard())
    return CREATE_DICT_STATE

