from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer, Index, Boolean, Text
import json

# Define SQLAlchemy ORM model for stores

Base = declarative_base()


class Store(Base):
    """ Class representing a store in the database. All chains in one table. """
    __tablename__ = "stores"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Chain info
    chain_code = Column(String, nullable=False)  # always provided
    chain_name = Column(String, nullable=True)  # optional if XML has it
    subchain_code = Column(String, nullable=True)
    subchain_name = Column(String, nullable=True)

    # Store info
    store_code = Column(String, nullable=False)  # always provided
    store_name = Column(String, nullable=True)
    store_type = Column(String, nullable=True)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    zipcode = Column(String, nullable=True)

    __table_args__ = (
        Index("ix_chain_code", "chain_code"),
        Index("ix_chain_store", "chain_code", "store_code", unique=True),
    )
