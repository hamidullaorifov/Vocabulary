from telegram import ReplyMarkup, Update, ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton,ReplyKeyboardRemove

def menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text='Find meaning',callback_data='find_meaning')],
        [InlineKeyboardButton(text='Find Word',callback_data='find_word')],
        [InlineKeyboardButton(text='New Dictionary',callback_data='new_dictionary')],
    ], resize_keyboard=True, one_time_keyboard=True)



def periods_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text='All',callback_data='period_all')],
        [InlineKeyboardButton(text='Random 20',callback_data='period_random20')],
        [InlineKeyboardButton(text='Last day',callback_data='period_lastday')],
        [InlineKeyboardButton(text='Last 3 days',callback_data='period_last3days')],
        [InlineKeyboardButton(text='Last Week',callback_data='period_lastweek')],
    ])


def back_to_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Back to menu",callback_data='back_to_menu')]])