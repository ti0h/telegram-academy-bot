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

# Словари для навигации "назад" (предыдущее состояние)
STUDENT_PREV = {
    StudentForm.race: StudentForm.name,
    StudentForm.age: StudentForm.race,
    StudentForm.gender_height_weight: StudentForm.age,
    StudentForm.character: StudentForm.gender_height_weight,
    StudentForm.abilities: StudentForm.character,
    StudentForm.weaknesses: StudentForm.abilities,
    StudentForm.facts: StudentForm.weaknesses,
    StudentForm.appearance: StudentForm.facts,
    StudentForm.biography: StudentForm.appearance,
    StudentForm.course: StudentForm.biography,
}

STAFF_PREV = {
    StaffForm.name: StaffForm.position,
    StaffForm.age: StaffForm.name,
    StaffForm.race: StaffForm.age,
    StaffForm.gender_height_weight: StaffForm.race,
    StaffForm.character: StaffForm.gender_height_weight,
    StaffForm.abilities: StaffForm.character,
    StaffForm.weaknesses: StaffForm.abilities,
    StaffForm.facts: StaffForm.weaknesses,
    StaffForm.appearance: StaffForm.facts,
    StaffForm.biography: StaffForm.appearance,
}

# Тексты вопросов для каждого состояния (используются при возврате "назад")
STUDENT_QUESTIONS = {
    StudentForm.name: (
        "<b>Имя</b>\nНазовись. Только без титулов."
    ),
    StudentForm.race: (
        "<b>Раса</b>\nИ кто ты у нас по природе? Человек, эльф, недодемон? "
        "Выбери из списка."
    ),
    StudentForm.age: (
        "<b>Возраст</b>\nНе подскажешь возраст? Мой я давно не считаю."
    ),
    StudentForm.gender_height_weight: (
        "<b>Пол / Рост / Вес</b>\nПол, рост, вес. Три скучных слова."
    ),
    StudentForm.character: (
        "<b>Характер</b>\nОпиши свой характер. Минимум 200 символов."
    ),
    StudentForm.abilities: (
        "<b>Способности</b>\nНа что ты способен? (без всесилия)"
    ),
    StudentForm.weaknesses: (
        "<b>Слабости и страхи</b>\nЧего ты боишься?"
    ),
    StudentForm.facts: (
        "<b>Факты</b>\nРазвлеки меня. Любимая еда, хобби, шрамы."
    ),
    StudentForm.appearance: (
        "<b>Внешность</b>\nОпиши, как выглядишь."
    ),
    StudentForm.biography: (
        "<b>Биография</b>\nОт восьми строк. Минимум 200 символов."
    ),
    StudentForm.course: (
        "<b>Курс</b>\nНа какой курс собрался?"
    ),
}

STAFF_QUESTIONS = {
    StaffForm.position: "<b>Должность</b>\nНапиши свою должность (например, «Учитель магии»).",
    StaffForm.name: "<b>Имя / Фамилия</b>\nПредставься.",
    StaffForm.age: "<b>Возраст</b>\nСколько тебе лет?",
    StaffForm.race: "<b>Раса</b>\nИ кто ты у нас по природе? Выбери из списка.",
    StaffForm.gender_height_weight: "<b>Пол / Рост / Вес</b>\nКто ты? пол, рост, вес.",
    StaffForm.character: "<b>Характер</b>\nРасскажи, с кем мне предстоит делить воздух. Минимум 200 символов.",
    StaffForm.abilities: "<b>Способности, магия и магическое направление</b>\nЧто ты умеешь?",
    StaffForm.weaknesses: "<b>Слабости, страхи</b>\nВсё выкладывай.",
    StaffForm.facts: "<b>Факты</b>\nПривычки, хобби, бывшие работы.",
    StaffForm.appearance: "<b>Внешность</b>\nКартинка или описание.",
    StaffForm.biography: "<b>Биография</b>\nГде учился, кого предавал. Минимум 200 символов.",
}
