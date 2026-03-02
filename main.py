import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import BotCommand
from aiogram.types import FSInputFile

photo1 = FSInputFile("img/пишу 1.jpg")
photo2 = FSInputFile("img/пишу 2.jpg")
photo3 = FSInputFile("img/пишу 3.jpg")
photo4 = FSInputFile("img/пишу 4.jpg")
photo5 = FSInputFile("img/пишу 5.jpg")
photo6 = FSInputFile("img/пишу 6.jpg")
photo7 = FSInputFile("img/пишу 7.jpg")
photo8 = FSInputFile("img/пишу 8.jpg")

# ================= НАСТРОЙКИ =================
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_USERNAME = "@ttrndsgn"
MANAGER_ID = 2091921011

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
@dp.message(F.text == "/help")
async def help_cmd(msg: Message):
    await msg.answer(
        "📞 Связь с менеджером: @ttrndsgn"
    )

@dp.message(CommandStart())
async def start(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer_photo(
        photo=photo1,
        caption=("Привет 👋\n\n"
        "Мы аккуратно переписываем конспекты от руки или составляем их за вас.\n\n"
        "📌 Важно:\n"
        "— мы НЕ решаем задачи\n"
        "— мы НЕ исправляем ошибки\n\n"
        "👉 Мы можем переписать задачи и формулы, если вы предоставите материал.\n\n"
        "Давайте начнём 👇"),
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

    await call.message.answer_photo(
        photo=photo4,
        caption="Что нужно сделать?",
        reply_markup=kb_tariff()
    )

@dp.callback_query(F.data.in_(["rewrite","summary"]))
async def choose_tariff(call: CallbackQuery, state: FSMContext):
    await state.update_data(tariff=call.data)
    # Просто отправляем новое сообщение
    await call.message.answer(
        "Нужны наши тетради?", 
        reply_markup=kb_yes_no("notebook")
    )
    await call.answer()  # Обязательно подтверждаем callback

@dp.callback_query(F.data.startswith("notebook_"))
async def notebook(call: CallbackQuery, state: FSMContext):
    await state.update_data(notebooks=call.data.endswith("yes"))
    
    # Отправляем новое сообщение с фото
    await call.message.answer_photo(
        photo=photo5,
        caption="Нужно срочно?",
        reply_markup=kb_yes_no("urgent")
    )
    await call.answer()  # Подтверждаем callback

@dp.callback_query(F.data.startswith("urgent_"))
async def urgent(call: CallbackQuery, state: FSMContext):
    await state.update_data(urgent=call.data.endswith("yes"))
    await call.answer()  # Подтверждаем callback

    # Отправляем сообщение с просьбой ввести количество страниц
    await call.message.answer_photo(
        photo=photo6,
        caption="Введите количество страниц цифрами (например: 5):",
    )
    
    # Устанавливаем состояние
    await state.set_state(Order.pages)
    print(f"Установлено состояние pages: {await state.get_state()}")  # Для отладки

@dp.message(Order.pages)
async def pages_input(msg: Message, state: FSMContext):
    # Проверяем текущее состояние для отладки
    current_state = await state.get_state()
    print(f"Состояние при вводе страниц: {current_state}")
    print(f"Получено сообщение: {msg.text}")
    
    # Проверяем, что введено число
    if not msg.text or not msg.text.isdigit():
        await msg.answer(
            "❌ Пожалуйста, введите число страниц цифрами.\n"
            "Например: 5, 10, 15"
        )
        return
    
    pages = int(msg.text)
    
    # Проверяем, что число положительное
    if pages <= 0:
        await msg.answer("❌ Количество страниц должно быть больше 0. Введите правильное число:")
        return
    
    if pages > 100:
        await msg.answer("⚠️ Максимальное количество страниц - 100. Введите число от 1 до 100:")
        return
    
    # Получаем все данные из состояния
    data = await state.get_data()
    print(f"Данные из состояния: {data}")
    
    # Проверяем, что все необходимые данные есть
    if 'tariff' not in data:
        await msg.answer("❌ Ошибка: не выбран тариф. Начните заново /start")
        await state.clear()
        return
    
    # Рассчитываем стоимость
    try:
        base = TARIFFS[data["tariff"]] * pages
        notebooks = 10 * pages if data.get("notebooks", False) else 0
        total = base + notebooks

        if data.get("urgent", False):
            total = int(total * 1.5)
    except Exception as e:
        print(f"Ошибка расчета: {e}")
        await msg.answer("❌ Ошибка расчета стоимости. Начните заново /start")
        await state.clear()
        return
    
    # Сохраняем данные
    await state.update_data(pages=pages, total=total)
    
    # Отправляем результат
    tariff_text = "Переписать" if data['tariff'] == 'rewrite' else "Составить конспект"
    urgent_text = "Да" if data.get('urgent', False) else "Нет"
    notebooks_text = "Да" if data.get('notebooks', False) else "Нет"
    
    await msg.answer_photo(
        photo=photo7,
        caption=(
            f"📊 Ваш заказ:\n\n"
            f"📄 Страниц: {pages}\n"
            f"📝 Тариф: {tariff_text}\n"
            f"⏱ Срочно: {urgent_text}\n"
            f"📓 Наши тетради: {notebooks_text}\n\n"
            f"💰 Итого: {total} ₽"
        ),
        reply_markup=kb_confirm()
    )
    
    # Состояние автоматически сохраняется, не сбрасываем его пока
@dp.callback_query(F.data == "confirm")
async def confirm(call: CallbackQuery, state: FSMContext):
    await call.answer()  # Подтверждаем callback
    
    # Отправляем НОВОЕ сообщение, не удаляя старое
    await call.message.answer(
        "✅ Отлично! Теперь отправьте материал:\n\n"
        "📎 Вы можете отправить:\n"
        "• Фото конспектов\n"
        "• Документ (PDF, Word)\n"
        "• Текстовое описание\n\n"
        "✍️ Опишите, что нужно сделать:"
    )
    await state.set_state(Order.materials)

@dp.callback_query(F.data == "edit")
async def edit_order(call: CallbackQuery, state: FSMContext):
    await call.answer()
    # Отправляем НОВОЕ сообщение, не удаляя старое
    await call.message.answer(
        "Что нужно сделать?",
        reply_markup=kb_tariff()
    )

@dp.message(Order.materials)
async def materials(msg: Message, state: FSMContext):
    # Получаем данные заказа
    data = await state.get_data()
    
    # Проверяем, что все необходимые данные есть
    if not data.get('user_type') or not data.get('subject') or not data.get('pages'):
        await msg.answer("❌ Ошибка: данные заказа повреждены. Начните заново /start")
        await state.clear()
        return
    
    # Формируем текст для менеджера
    user_type = "Школьник" if data["user_type"] == "school" else "Студент"
    tariff = "Переписать" if data["tariff"] == "rewrite" else "Составить конспект"
    notebooks = "Да" if data.get("notebooks", False) else "Нет"
    urgent = "Да" if data.get("urgent", False) else "Нет"
    
    # Информация о клиенте
    client_info = f"@{msg.from_user.username}" if msg.from_user.username else "Нет username"
    
    text = (
        f"📥 НОВЫЙ ЗАКАЗ\n\n"
        f"👤 Клиент: {client_info}\n"
        f"🆔 ID: {msg.from_user.id}\n"
        f"📱 Имя: {msg.from_user.full_name}\n\n"
        f"🎓 Тип: {user_type}\n"
        f"📚 Предмет: {data.get('subject', 'Не указан')}\n\n"
        f"📝 Тариф: {tariff}\n"
        f"📓 Наши тетради: {notebooks}\n"
        f"⏱ Срочно: {urgent}\n\n"
        f"📄 Страниц: {data.get('pages', 0)}\n"
        f"💰 Сумма: {data.get('total', 0)} ₽\n\n"
        f"📎 Материалы клиента:"
    )

    try:
        # Отправляем информацию менеджеру
        await bot.send_message(MANAGER_ID, text)
        
        # Пересылаем сообщение с материалами
        await msg.forward(MANAGER_ID)
        
        # Если это фото или документ, можно отправить отдельно для лучшего качества
        if msg.photo:
            await bot.send_message(MANAGER_ID, "📸 Фото материалов:")
        elif msg.document:
            await bot.send_message(MANAGER_ID, "📎 Документ с материалами:")
            
    except Exception as e:
        print("Ошибка отправки менеджеру:", e)
        await msg.answer("⚠ Ошибка связи с менеджером. Мы уже решаем проблему.\nПожалуйста, попробуйте позже или свяжитесь напрямую: @ttrndsgn")
        return

    # Подтверждение клиенту
    await msg.answer_photo(
        photo=photo8,
        caption=(
            "✅ Заявка принята!\n\n"
            "Менеджер скоро с вами свяжется.\n"
            f"Менеджер: {MANAGER_USERNAME}\n\n"
            "Пожалуйста, ожидайте ответа в ближайшее время."
        )
    )

    # Очищаем состояние
    await state.clear()

# ================= ЗАПУСК =================

async def main():
    await set_commands(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":

    asyncio.run(main())










