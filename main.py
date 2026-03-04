import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import BotCommand
from aiogram.types import FSInputFile
from aiogram.fsm.storage.memory import MemoryStorage

photo1 = FSInputFile("img/1.jpg")
photo2 = FSInputFile("img/2.jpg")
photo3 = FSInputFile("img/3.jpg")
photo4 = FSInputFile("img/4.jpg")
photo5 = FSInputFile("img/5.jpg")
photo6 = FSInputFile("img/6.jpg")
photo7 = FSInputFile("img/7.jpg")
photo8 = FSInputFile("img/8.jpg")

# ================= НАСТРОЙКИ =================
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_USERNAME = "@DimentiySobolev"
MANAGER_ID = 785215907

TARIFFS = {
    "rewrite": 20,
    "summary": 50
}


class Order(StatesGroup):
    user_type = State()
    subject = State()
    tariff = State()
    notebooks = State()
    urgent = State()
    pages = State()
    materials = State()

# ================= БОТ =================
print("БОТ ЗАПУЩЕН")
bot = Bot(BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ================= КНОПКИ =================
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Перезапустить бота"),
        BotCommand(command="help", description="Связь с менеджером"),
    ]
    await bot.set_my_commands(commands)

def kb_user_type():
    kb = InlineKeyboardBuilder()
    kb.button(text="📚 Я школьник", callback_data="school")
    kb.button(text="🎓 Я студент", callback_data="student")
    return kb.as_markup()

def kb_subjects(user_type):
    school = ["Русский","История","Биология","География","Общество","Литература","Иностранный","Другой"]
    student = ["История","Философия","Психология","Право","Экономика","Менеджмент","Педагогика","Другой"]
    kb = InlineKeyboardBuilder()
    for s in school if user_type == "school" else student:
        kb.button(text=s, callback_data=f"sub_{s}")
    kb.adjust(2)
    return kb.as_markup()

def kb_continue():
    kb = InlineKeyboardBuilder()
    kb.button(text="👉 Поехали", callback_data="go")
    return kb.as_markup()

def kb_tariff():
    kb = InlineKeyboardBuilder()
    kb.button(text="✍ Переписать", callback_data="rewrite")
    kb.button(text="📖 Составить конспект", callback_data="summary")
    kb.adjust(1)
    return kb.as_markup()

def kb_yes_no(prefix):
    kb = InlineKeyboardBuilder()
    kb.button(text="Да", callback_data=f"{prefix}_yes")
    kb.button(text="Нет", callback_data=f"{prefix}_no")
    return kb.as_markup()

def kb_confirm():
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Оформить заказ", callback_data="confirm")
    return kb.as_markup()

'''def kb_confirm():
    kb = InlineKeyboardBuilder()
    kb.button(text="Оформить", callback_data="confirm")
    kb.button(text="Изменить заказ", callback_data="edit")
    return kb.as_markup()'''

# ================= ЛОГИКА =================

@dp.message(F.text == "/help")
async def help_cmd(msg: Message):
    await msg.answer("📞 Связь с менеджером: @DimentiySobolev")

@dp.message(CommandStart())
async def start(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer_photo(
        photo=photo1,
        caption=(
            "Привет 👋\n\n"
            "Мы аккуратно переписываем конспекты от руки или составляем их за вас.\n\n"
            "📌 Важно:\n"
            "— мы НЕ решаем задачи\n"
            "— мы НЕ исправляем ошибки\n\n"
            "👉 Мы можем переписать задачи и формулы, если вы предоставите материал.\n\n"
            "Давайте начнём 👇"
        ),
        reply_markup=kb_user_type()
    )

@dp.callback_query(F.data.in_(["school","student"]))
async def choose_type(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(user_type=call.data)
    await call.message.answer_photo(
        photo=photo2,
        caption="Выберите предмет:",
        reply_markup=kb_subjects(call.data)
    )

@dp.callback_query(F.data.startswith("sub_"))
async def choose_subject(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(subject=call.data[4:])
    await call.message.answer_photo(
        photo=photo3,
        caption=(
            "❗ Важно:\n\n"
            "Мы НЕ выполняем:\n"
            "— решение задач\n"
            "— примеры и уравнения\n"
            "— расчёты\n"
            "— исправление текста\n\n"
            "✔ Но можем переписать материал.\n\n"
            "Мы выполняем:\n"
            "— переписывание\n"
            "— оформление конспектов\n"
            "— составление конспектов"
        ),
        reply_markup=kb_continue()
    )

@dp.callback_query(F.data == "go")
async def go(call: CallbackQuery):
    await call.answer()
    await call.message.answer_photo(
        photo=photo4,
        caption="Что нужно сделать?",
        reply_markup=kb_tariff()
    )

@dp.callback_query(F.data.in_(["rewrite","summary"]))
async def choose_tariff(call: CallbackQuery, state: FSMContext):
    print("Тариф выбран:", call.data)
    await call.answer()
    await state.update_data(tariff=call.data)
    await call.message.answer("Нужны наши тетради?", reply_markup=kb_yes_no("notebook"))

@dp.callback_query(F.data.startswith("notebook_"))
async def notebook(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(notebooks=call.data.endswith("yes"))
    await call.message.answer_photo(
        photo=photo5,
        caption="Нужно срочно?",
        reply_markup=kb_yes_no("urgent")
    )

@dp.callback_query(F.data.startswith("urgent_"))
async def urgent(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(urgent=call.data.endswith("yes"))
    await call.message.answer_photo(
        photo=photo6,
        caption="Введите количество страниц цифрами:"
    )
    await state.set_state(Order.pages)

@dp.message(Order.pages, F.text)
async def pages_input(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer("Введите число страниц цифрами:")
        return

    pages = int(msg.text)
    data = await state.get_data()

    base = TARIFFS[data["tariff"]] * pages
    notebooks = 10 * pages if data.get("notebooks") else 0
    total = base + notebooks
    if data.get("urgent"):
        total = int(total * 1.5)

    await state.update_data(pages=pages, total=total)

    await msg.answer_photo(
        photo=photo7,
        caption=(
            f"📄 Страниц: {pages}\n"
            f"💰 Итого: {total} ₽"
        ),
        reply_markup=kb_confirm()
    )

@dp.callback_query(F.data == "confirm")
async def confirm(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer("Отправьте материал:")
    await state.set_state(Order.materials)

'''@dp.callback_query(F.data == "edit")
async def edit_order(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer("Что нужно сделать?", reply_markup=kb_tariff())'''

@dp.message(Order.materials)
async def materials(msg: Message, state: FSMContext):
    data = await state.get_data()

    await bot.send_message(MANAGER_ID, f"Новый заказ от @{msg.from_user.username}")
    await msg.forward(MANAGER_ID)

    await msg.answer_photo(
        photo=photo8,
        caption="✅ Заявка принята! Менеджер скоро с вами свяжется."
    )

    await state.clear()

# ================= ЗАПУСК =================

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await set_commands(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())





