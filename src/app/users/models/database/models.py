from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from src.app.database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    mobile_number = Column(String)
    password = Column(String)
    slips = relationship("Slip", backref="user")

    __table_args__ = (UniqueConstraint('email', name='users_uc'), )
