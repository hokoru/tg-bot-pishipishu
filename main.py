import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import BotCommand
from yookassa import Configuration, Payment
from aiogram.types import FSInputFile
import uuid

photo1 = FSInputFile("пишу 1.jpg")
photo2 = FSInputFile("пишу 2.jpg")
photo3 = FSInputFile("пишу 3.jpg")
photo4 = FSInputFile("пишу 4.jpg")
photo5 = FSInputFile("пишу 5.jpg")
photo6 = FSInputFile("пишу 6.jpg")
photo7 = FSInputFile("пишу 7.jpg")
photo8 = FSInputFile("пишу 8.jpg")

# ================= НАСТРОЙКИ =================
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_USERNAME = "@ttrndsgn"
MANAGER_ID = 2091921011

TARIFFS = {
    "rewrite": 20,
    "summary": 50
}

SHOP_ID = os.getenv("SHOP_ID")
SECRET_KEY = os.getenv("SECRET_KEY")

Configuration.account_id = SHOP_ID
Configuration.secret_key = SECRET_KEY
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

def kb_pay(url):
    kb = InlineKeyboardBuilder()
    kb.button(text="💳 Оплатить", url=url)
    kb.button(text="✅ Я оплатил", callback_data="check_payment")
    return kb.as_markup()

def create_payment(amount, description):
    payment = Payment.create({
        "amount": {
            "value": f"{amount}.00",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/"
        },
        "capture": True,
        "description": description,
        "metadata": {
            "order_id": str(uuid.uuid4())
        }
    })
    return payment.confirmation.confirmation_url, payment.id


# ================= ЛОГИКА =================
@dp.message(F.text == "/help")
async def help_cmd(msg: Message):
    await msg.answer(
        "📞 Связь с менеджером: @kadringeer"
    )

@dp.message(CommandStart())
async def start(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer_photo(
        photo=photo1,
        caption='''Привет 👋\n\n
        Мы аккуратно переписываем конспекты от руки или составляем их за вас.\n
        📌 Важно:
        — мы НЕ решаем задачи
        — мы НЕ исправляем ошибки\n
        👉 Мы можем переписать задачи и формулы, если вы предоставите материал.\n
        Давайте начнём 👇''',
        reply_markup=kb_user_type()
    )

@dp.callback_query(F.data.in_(["school","student"]))
async def choose_type(call: CallbackQuery, state: FSMContext):
    await state.update_data(user_type=call.data)

    await call.message.answer_photo(
        photo=photo2,
        caption="Выберите предмет:",
        reply_markup=kb_subjects(call.data)
    )

@dp.callback_query(F.data.startswith("sub_"))
async def choose_subject(call: CallbackQuery, state: FSMContext):
    await state.update_data(subject=call.data[4:])

    await call.message.delete()


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
    await call.message.delete()


    await call.message.answer_photo(
        photo=photo3,
        caption="Что нужно сделать?",
        reply_markup=kb_tariff()
    )

@dp.callback_query(F.data.in_(["rewrite","summary"]))
async def choose_tariff(call: CallbackQuery, state: FSMContext):
    await state.update_data(tariff=call.data)
    await call.message.edit_text("Нужны наши тетради?", reply_markup=kb_yes_no("notebook"))

@dp.callback_query(F.data.startswith("notebook_"))
async def notebook(call: CallbackQuery, state: FSMContext):
    await state.update_data(notebooks=call.data.endswith("yes"))

    await call.message.delete()


    await call.message.answer_photo(
        photo=photo5,
        caption="Нужно срочно?",
        reply_markup=kb_yes_no("urgent")
    )

@dp.callback_query(F.data.startswith("urgent_"))
async def urgent(call: CallbackQuery, state: FSMContext):
    await state.update_data(urgent=call.data.endswith("yes"))

    await call.message.delete()


    await call.message.answer_photo(
        photo=photo6,
        caption="Введите количество страниц:",
    )

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

    await msg.answer_photo(
        caption=("📊 Ваш заказ:\n\n"
        f"Страниц: {pages}\n"
        f"Тариф: {'Переписать' if data['tariff']=='rewrite' else 'Составить конспект'}\n"
        f"Срочность: {'Да' if data['urgent'] else 'Нет'}\n"
        f"Тетради: {'Да' if data['notebooks'] else 'Нет'}\n\n"
        f"💰 Итого: {total} ₽"),
        photo=photo7,
        reply_markup=kb_confirm()
    )

@dp.callback_query(F.data == "edit")
async def edit(call: CallbackQuery):
    await call.message.edit_text("Что нужно сделать?", reply_markup=kb_tariff())

@dp.callback_query(F.data == "confirm")
async def confirm(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    pay_url, pay_id = create_payment(
        data["total"],
        f"Заказ ПишиПишу — {call.from_user.id}"
    )

    await state.update_data(payment_id=pay_id)

    await call.message.edit_text(
        f"💰 К оплате: {data['total']} ₽\n\n"
        "Нажмите кнопку ниже для оплаты 👇",
        reply_markup=kb_pay(pay_url)
    )

@dp.callback_query(F.data == "check_payment")
async def check_payment(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    payment = Payment.find_one(data["payment_id"])

    if payment.status == "succeeded":
        await call.message.edit_text("✅ Оплата получена!\n\nОтправьте материал:")
        await state.set_state(Order.materials)
    else:
        await call.answer("❌ Платёж не найден. Попробуйте позже.", show_alert=True)

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

    await msg.answer_photo(
        caption=("✅ Заявка принята!\n\n"
        "Менеджер скоро с вами свяжется.\n"
        f"Менеджер: {MANAGER_USERNAME}"),
        photo=photo8
    )

    await state.clear()

# ================= ЗАПУСК =================

async def main():
    await set_commands(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":

    asyncio.run(main())



