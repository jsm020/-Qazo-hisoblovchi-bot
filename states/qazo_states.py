from aiogram.dispatcher.filters.state import State, StatesGroup

class QazoStates(StatesGroup):
    waiting_for_years = State()
    waiting_for_manual_input = State()
