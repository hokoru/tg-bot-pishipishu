import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import BotCommand

# ================= НАСТРОЙКИ =================
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_USERNAME = "@skufchanskiy"
MANAGER_ID = 8034034918

TARIFFS = {
    "rewrite": 20,
    "summary": 50
}

# ================= СОСТОЯНИЯ =================

class Order(StatesGroup):
    user_type = State()
    subject = State()
    tariff = State()
    notebooks = State()
    urgent = State()
    pages = State()
    materials = State()

# ================= БОТ =================

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

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
    kb.button(text="Оформить", callback_data="confirm")
    kb.button(text="Изменить заказ", callback_data="edit")
    return kb.as_markup()

# ================= ЛОГИКА =================
@dp.message()
async def debug(msg: Message):
    print(msg.from_user.id)

@dp.message(F.text == "/help")
async def help_cmd(msg: Message):
    await msg.answer(
        "📞 Связь с менеджером: @kadringeer"
    )

@dp.message(CommandStart())
async def start(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        "Привет 👋\n\n"
        "Мы аккуратно переписываем конспекты от руки или составляем их за вас.\n\n"
        "📌 Важно:\n"
        "— мы НЕ решаем задачи\n"
        "— мы НЕ исправляем ошибки\n\n"
        "👉 Мы можем переписать задачи и формулы, если вы предоставите материал.\n\n"
        "Давайте начнём 👇",
        reply_markup=kb_user_type()
    )

@dp.callback_query(F.data.in_(["school","student"]))
async def choose_type(call: CallbackQuery, state: FSMContext):
    await state.update_data(user_type=call.data)
    await call.message.edit_text("Выберите предмет:", reply_markup=kb_subjects(call.data))

@dp.callback_query(F.data.startswith("sub_"))
async def choose_subject(call: CallbackQuery, state: FSMContext):
    await state.update_data(subject=call.data[4:])
    await call.message.edit_text(
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
        "— составление конспектов",
        reply_markup=kb_continue()
    )

@dp.callback_query(F.data == "go")
async def go(call: CallbackQuery):
    await call.message.edit_text("Что нужно сделать?", reply_markup=kb_tariff())

@dp.callback_query(F.data.in_(["rewrite","summary"]))
async def choose_tariff(call: CallbackQuery, state: FSMContext):
    await state.update_data(tariff=call.data)
    await call.message.edit_text("Нужны наши тетради?", reply_markup=kb_yes_no("notebook"))

@dp.callback_query(F.data.startswith("notebook_"))
async def notebook(call: CallbackQuery, state: FSMContext):
    await state.update_data(notebooks=call.data.endswith("yes"))
    await call.message.edit_text("Нужно срочно?", reply_markup=kb_yes_no("urgent"))

@dp.callback_query(F.data.startswith("urgent_"))
async def urgent(call: CallbackQuery, state: FSMContext):
    await state.update_data(urgent=call.data.endswith("yes"))
    await call.message.edit_text("Введите количество страниц:")
    await state.set_state(Order.pages)

@dp.message(Order.pages)
async def calc(msg: Message, state: FSMContext):
    if msg.text.lower() == "оператор":
        await msg.answer(f"Связь с менеджером: {MANAGER_USERNAME}")
        return

    if not msg.text.isdigit():
        await msg.answer("Введите число страниц:")
        return

    pages = int(msg.text)
    data = await state.get_data()

    base = TARIFFS[data["tariff"]] * pages
    notebooks = 10 * pages if data["notebooks"] else 0
    total = base + notebooks

    if data["urgent"]:
        total = int(total * 1.5)

    await state.update_data(pages=pages, total=total)

    await msg.answer(
        f"📊 Ваш заказ:\n\n"
        f"Страниц: {pages}\n"
        f"Тариф: {'Переписать' if data['tariff']=='rewrite' else 'Составить конспект'}\n"
        f"Срочность: {'Да' if data['urgent'] else 'Нет'}\n"
        f"Тетради: {'Да' if data['notebooks'] else 'Нет'}\n\n"
        f"💰 Итого: {total} ₽",
        reply_markup=kb_confirm()
    )

@dp.callback_query(F.data == "edit")
async def edit(call: CallbackQuery):
    await call.message.edit_text("Что нужно сделать?", reply_markup=kb_tariff())

@dp.callback_query(F.data == "confirm")
async def confirm(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Отлично 👍\n\nОтправьте материал:")
    await state.set_state(Order.materials)

@dp.message(Order.materials)
async def materials(msg: Message, state: FSMContext):
    data = await state.get_data()

    user_type = "Школьник" if data["user_type"] == "school" else "Студент"
    tariff = "Переписать" if data["tariff"] == "rewrite" else "Составить конспект"
    notebooks = "Да" if data["notebooks"] else "Нет"
    urgent = "Да" if data["urgent"] else "Нет"

    text = (
        f"📥 НОВЫЙ ЗАКАЗ\n\n"
        f"👤 Клиент: @{msg.from_user.username}\n"
        f"🆔 ID: {msg.from_user.id}\n\n"
        f"🎓 Тип: {user_type}\n"
        f"📚 Предмет: {data['subject']}\n\n"
        f"📝 Тариф: {tariff}\n"
        f"📓 Наши тетради: {notebooks}\n"
        f"⏱ Срочно: {urgent}\n\n"
        f"📄 Страниц: {data['pages']}\n"
        f"💰 Сумма: {data['total']} ₽"
    )

    try:
        await bot.send_message(MANAGER_ID, text)
        await msg.forward(MANAGER_ID)
    except Exception as e:
        print("Ошибка отправки менеджеру:", e)
        await msg.answer("⚠ Ошибка связи с менеджером. Мы уже решаем проблему.")
        return

    await msg.answer(
        "✅ Заявка принята!\n\n"
        "Менеджер скоро с вами свяжется.\n"
        f"Менеджер: {MANAGER_USERNAME}"
    )

    await state.clear()

# ================= ЗАПУСК =================

async def main():
    await set_commands(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":

    asyncio.run(main())


