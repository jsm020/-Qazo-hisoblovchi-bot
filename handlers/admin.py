from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import add_faq, create_faq_table
from config import ADMINS

router = Router()

class AddFAQState(StatesGroup):
    waiting_for_question = State()
    waiting_for_answer = State()

@router.message(F.text == "/admin")
async def admin_panel(message: Message):
    await message.answer("Admin panel")

@router.message(F.text == "/addfaq")
async def add_faq_start(message: Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        await message.answer("Faqat adminlar savol qo'sha oladi.")
        return
    await message.answer("Yangi savol matnini yuboring:")
    await state.set_state(AddFAQState.waiting_for_question)

@router.message(AddFAQState.waiting_for_question)
async def add_faq_question(message: Message, state: FSMContext):
    await state.update_data(question=message.text)
    await message.answer("Endi ushbu savolga javobni yuboring:")
    await state.set_state(AddFAQState.waiting_for_answer)

@router.message(AddFAQState.waiting_for_answer)
async def add_faq_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    question = data["question"]
    answer = message.text
    await add_faq(question, answer)
    await message.answer("Savol va javob muvaffaqiyatli qo'shildi!")
    await state.clear()

# Bot ishga tushganda jadval yaratilishi uchun
@router.startup()
async def on_startup():
    await create_faq_table()

def register_admin_handlers(dp):
    dp.include_router(router)
