from aiogram.fsm.state import State, StatesGroup

class FSMFillProfile(StatesGroup):
    yes_no_fillprofile = State()
    fill_name = State()
    fill_city = State()
    fill_text = State()
    fill_musician_type = State()
    fill_interest = State()
    upload_photo = State()
    main_menu = State()