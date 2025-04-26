import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy_utils import force_instant_defaults
from pydantic import BaseModel, Field
from typing import Annotated

engine = sa.create_engine("sqlite:////Users\malac\Documents\Productivity\Databases\MoneySimulator.db", connect_args={"check_same_thread": False})
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
force_instant_defaults()

def getDatabase():
    db = Session()
    try:
        yield db
    finally:
        db.close()

class PetDataModel(BaseModel):
    id: str
    count: int
    transactions: list[Annotated[int, Field(strict=True, gt=0)]]

class UpdateDataModel(BaseModel):
    data: list[PetDataModel]

class PetData(Base):
    __tablename__ = 'PetData'

    id = sa.Column(sa.String, primary_key=True)
    count = sa.Column(sa.Integer, default=0)
    value = sa.Column(sa.Integer, default=0)
    transactions = sa.Column(sa.JSON, default=[])

Base.metadata.create_all(bind=engine)
