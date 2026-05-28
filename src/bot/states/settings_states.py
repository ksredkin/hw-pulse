from aiogram.fsm.state import State, StatesGroup


class UpdateOverheatAlertTemp(StatesGroup):
    waiting_for_temp = State()
