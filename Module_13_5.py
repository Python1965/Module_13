# Домашнее задание по теме "Клавиатура кнопок".
# *****************************************************************************************************************
# Исользуются
#   Python версии 3.9.13
#   Aiogram версии 2.25.1
#
# Задача "Меньше текста, больше кликов":
#
# Необходимо дополнить код предыдущей задачи, чтобы вопросы о параметрах тела для расчёта калорий
# выдавались по нажатию кнопки.
#   1. Измените massage_handler для функции set_age. Теперь этот хэндлер будет реагировать на текст
#      'Рассчитать', а не на 'Calories'.
#   2. Создайте клавиатуру ReplyKeyboardMarkup и 2 кнопки KeyboardButton на ней со следующим текстом:
#      'Рассчитать' и 'Информация'. Сделайте так, чтобы клавиатура подстраивалась под размеры
#      интерфейса устройства при помощи параметра resize_keyboard.
#   3. Используйте ранее созданную клавиатуру в ответе функции start, используя параметр reply_markup.
#
# В итоге при команде /start у вас должна присылаться клавиатура с двумя кнопками. При нажатии
# на кнопку с надписью 'Рассчитать' срабатывает функция set_age с которой начинается работа
# машины состояний для age, growth и weight.
# *****************************************************************************************************************

from aiogram import Bot, Dispatcher,executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True) # инициализация клавиатуры
button = KeyboardButton(text='Информация')
button2 = KeyboardButton(text='Рассчитать')
kb.row(button)
kb.row(button2)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет!  Я бот помогающий твоему здоровью.', reply_markup=kb)

@dp.message_handler(text='Информация')
async def inform(message):
    await message.answer('На текущий момент я пока только могу рассчитать необходимое количество килокалорий (ккал) '
                         'в сутки для каждого конкретного человека. \n По формулуe Миффлина-Сан Жеора, разработанной '
                         'группой американских врачей-диетологов под руководством докторов Миффлина и Сан Жеора. \n'
                         'Погнали!? - жми кнопку Рассчитать')

@dp.message_handler(text='Рассчитать')
async def set_age(message):
    await message.answer('Введите свой возраст:')
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
    result = (10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age']) + 5)
    await message.answer(f'Ваша норма калорий: {result} ккал в сутки (для мужчин)')
    await UserState.weight.set()
    await state.finish()


@dp.message_handler()
async def all_message(message):
    # print('Введите команду /start, чтобы начать общение.')
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
