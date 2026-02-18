import streamlit as st

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
import asyncio

from backend.app.db.models import Base, Store

# DATABASE_URL = st.secrets["DATABASE_URL"]
DATABASE_URL = st.secrets.get("DATABASE_URL")


def get_engine(database_url: str = DATABASE_URL):
    """ Create and return an asynchronous SQLAlchemy engine. """
    engine = create_async_engine(database_url, echo=True, pool_pre_ping=True,
                                 connect_args={
                                     "statement_cache_size": 0, },  # 🔑 REQUIRED for Supabase
                                 )
    return engine


async def get_session() -> AsyncSession:
    """ Create and return an asynchronous SQLAlchemy session. """
    engine = get_engine()
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    return async_session()


