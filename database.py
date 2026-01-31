import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy_utils import force_instant_defaults
from pydantic import BaseModel, Field
from typing import Annotated
from enum import Enum
import dotenv
import os

dotenv.load_dotenv(dotenv.find_dotenv())

dbURI = os.environ.get('DB_URI')

engine = sa.create_engine(dbURI)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
force_instant_defaults()

def getDatabase():
    db = Session()
    try:
        yield db
    finally:
        db.close()

ItemType =  Enum(
    'ItemType',
    ((value, value) for value in ["Pet", "Item"]),
    type=str
)

class ItemDataModel(BaseModel):
    id: str
    itemType: ItemType
    count: int
    baseValue: float
    transactions: list[Annotated[list, [Annotated[float, Field(strict=True, gt=0)], Annotated[float, Field(strict=True, gt=0)]]]]

class NewDataModel(BaseModel):
    data: list[ItemDataModel]

class ItemData(Base):
    __tablename__ = 'ItemData'

    id = sa.Column(sa.String(50), primary_key=True)
    itemType = sa.Column(sa.String(50), default="Pet")
    count = sa.Column(sa.Integer, default=0)
    value = sa.Column(sa.Float, default=0)
    baseValue = sa.Column(sa.Float, default=0)
    transactions = sa.Column(sa.JSON, default=[])


Base.metadata.create_all(bind=engine)
