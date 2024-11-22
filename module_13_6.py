from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = ''
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()



keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
button_calculate = KeyboardButton('Рассчитать')
button_info = KeyboardButton('Информация')
keyboard.add(button_calculate, button_info)


inline_keyboard = InlineKeyboardMarkup(row_width=2)
button_calories = InlineKeyboardButton('Рассчитать норму калорий', callback_data='calories')
button_formulas = InlineKeyboardButton('Формулы расчёта', callback_data='formulas')
inline_keyboard.add(button_calories, button_formulas)


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply('Привет! Я бот, помогающий твоему здоровью.\nВыберите действие:', reply_markup=keyboard)


@dp.message_handler(lambda message: message.text.lower() == 'рассчитать')
async def main_menu(message: types.Message):
    await message.reply('Выберите опцию:', reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda call: call.data == 'formulas')
async def get_formulas(call: types.CallbackQuery):
    await call.message.reply(
        "Формула Миффлина-Сан Жеора:\n\nДля женщин:\nBMR = 10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (лет) - 161\n\nДля мужчин:\nBMR = 10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (лет) + 5")


@dp.callback_query_handler(lambda call: call.data == 'calories')
async def ask_age(call: types.CallbackQuery):
    await call.message.reply('Введите свой возраст:')
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def ask_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.reply('Введите свой рост (в см):')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def ask_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=message.text)
    await message.reply('Введите свой вес (в кг):')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def calculate_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text)
    data = await state.get_data()

    age = int(data.get('age'))
    growth = float(data.get('growth'))
    weight = float(data.get('weight'))

   
    calories = 10 * weight + 6.25 * growth - 5 * age - 161
    await message.reply(f'Ваши калории: {calories:.2f}', reply_markup=keyboard)
    await state.finish()


@dp.message_handler(lambda message: message.text.lower() == 'информация')
async def show_info(message: types.Message):
    await message.reply("Я бот, который помогает рассчитывать ваши калории. Нажмите 'Рассчитать', чтобы начать!",
                        reply_markup=keyboard)


@dp.message_handler(lambda message: True)
async def fallback(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.reply("Для начала работы с ботом введите /start или нажмите 'Рассчитать'.", reply_markup=keyboard)
    else:
        await message.reply("Пожалуйста, следуйте инструкциям и введите данные в нужном формате.",
                            reply_markup=keyboard)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
