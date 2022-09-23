from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()
class Loss(Base):
    __tablename__ = "Losses"
    id = Column(Integer, primary_key=True)
    discordId = Column(String, unique=True, nullable=False)
    discordUsername = Column(String, nullable=False)
    goldLost = Column(Integer, nullable=False)
    description = Column(String, nullable=False)