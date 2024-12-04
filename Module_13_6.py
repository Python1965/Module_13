# Домашнее задание по теме "Инлайн клавиатуры".
# *****************************************************************************************************************
# Исользуются
#   Python версии 3.9.13
#   Aiogram версии 2.25.1
#
# Задача "Ещё больше выбора":
#
# Необходимо дополнить код предыдущей задачи, чтобы при нажатии на кнопку 'Рассчитать'
# присылалась  Inline-клавиатуhа.
# Создайте клавиатуру InlineKeyboardMarkup с 2 кнопками InlineKeyboardButton:
#   1. С текстом 'Рассчитать норму калорий' и callback_data='calories'
#   2. С текстом 'Формулы расчёта' и callback_data='formulas'
#
# Создайте новую функцию main_menu(message), которая:
#   1. Будет обёрнута в декоратор message_handler, срабатывающий при передаче текста 'Рассчитать'.
#   2. Сама функция будет присылать ранее созданное Inline меню и текст 'Выберите опцию:'
#
# Создайте новую функцию get_formulas(call), которая:
#   1. Будет обёрнута в декоратор callback_query_handler, который будет реагировать
#      на текст 'formulas'.
#   2. Будет присылать сообщение с формулой Миффлина-Сан Жеора.
#
# Измените функцию set_age и декоратор для неё:
#   1. Декоратор смените на callback_query_handler, который будет реагировать на текст 'calories'.
#   2. Теперь функция принимает не message, а call. Доступ к сообщению будет следующим - call.message.
#
# По итогу получится следующий алгоритм:
#   1. Вводится команда /start
#   2. На эту команду присылается обычное меню: 'Рассчитать' и 'Информация'.
#   3. В ответ на кнопку 'Рассчитать' присылается Inline меню: 'Рассчитать норму калорий'
#      и 'Формулы расчёта'
#   4. По Inline кнопке 'Формулы расчёта' присылается сообщение с формулой.
#   5. По Inline кнопке 'Рассчитать норму калорий' начинает работать машина состояний по цепочке.
# *****************************************************************************************************************

from aiogram import Bot, Dispatcher,executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())


# ------ Марк ап клавиатура (с кнопками)----------------
kb = ReplyKeyboardMarkup(resize_keyboard=True)
button = KeyboardButton(text='Информация')
button2 = KeyboardButton(text='Рассчитать')
kb.row(button)
kb.row(button2)

#-------- Ин лайн клавиатура (с кнопками)----------------
kb2 = InlineKeyboardMarkup()
in_button1 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
in_button2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kb2.add(in_button1)
kb2.add(in_button2)

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=kb)

@dp.message_handler(text='Информация')
async def inform(message):
    await message.answer('На текущий момент я пока только могу рассчитать необходимое количество килокалорий (ккал) '
                         'в сутки для каждого конкретного человека. \n По формулуe Миффлина-Сан Жеора, разработанной '
                         'группой американских врачей-диетологов под руководством докторов Миффлина и Сан Жеора. \n'
                         'Погнали!? - жми кнопку Рассчитать')

@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=kb2)

@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('для мужчин: 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5;'
                              '\nдля женщин: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161')
    await call.answer()

@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Данные необходимо вводить целыми числами')
    await call.message.answer('Введите свой возраст:')
    await call.answer()
    await UserState.age.set()

@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост:')
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    mans = (10*int(data['weight'])+6.25*int(data['growth'])-5*int(data['age'])+5)
    wumans = (10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age']) - 161)
    await message.answer(f'При таких параметрах норма калорий: \nдля мужчин {mans} ккал в сутки \nдля женщин {wumans} ккал в сутки')
    await UserState.weight.set()
    await state.finish()

@dp.message_handler()
async def all_message(message):
    # print('Введите команду /start, чтобы начать общение.')
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)