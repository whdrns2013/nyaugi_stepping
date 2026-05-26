from config.enums import DUPLICATION
from engine.db_engine import get_db_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from models.step_data import User

GLOBAL_DB_ENGINE = get_db_engine()

def retrieve_all_user_emails(engine=GLOBAL_DB_ENGINE):
    Session = sessionmaker(bind=engine)
    
    with Session() as s:
        smtm = select(User.email)
        datas = s.scalars(smtm).all()
    return datas

def check_email(input_email:str):
    exist_emails = retrieve_all_user_emails()
    if input_email in exist_emails:
        return DUPLICATION.DUPLICATED
    else:
        return DUPLICATION.VALID