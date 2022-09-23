from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()
class Win(Base):
    __tablename__ = "Wins"
    id = Column(Integer, primary_key=True)
    discordId = Column(String, nullable=False)
    discordUsername = Column(String, nullable=False)
    goldSaved = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
