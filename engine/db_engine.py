from config.config import config
from sqlalchemy import create_engine
import streamlit as st

def get_db_engine():
    if config["service"]["mode"] == "dev":
        engine = create_engine(config["db"]["url"])
        return engine
    elif config["service"]["mode"] == "prod":
        db_url = st.secrets["SUPABASE_DB_URL"]
        engine = create_engine(db_url)
        return engine
    