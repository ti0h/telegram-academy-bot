from aiogram.fsm.state import State, StatesGroup

class Choice(StatesGroup):
    waiting = State()

class StudentForm(StatesGroup):
    name = State()
    race = State()
    age = State()
    gender_height_weight = State()
    character = State()
    abilities = State()
    weaknesses = State()
    facts = State()
    appearance = State()
    biography = State()
    course = State()

class StaffForm(StatesGroup):
    position = State()
    name = State()
    age = State()
    race = State()
    gender_height_weight = State()
    character = State()
    abilities = State()
    weaknesses = State()
    facts = State()
    appearance = State()
    biography = State()

class RejectReason(StatesGroup):
    waiting_for_reason = State()
