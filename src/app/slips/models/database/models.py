from sqlalchemy import Column, Integer, String, UniqueConstraint, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from src.app.database import Base

class Slip(Base):
    __tablename__ = 'slips'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    media_item_id = Column(Integer, ForeignKey('media_items.id'))
    unique_id = Column(String)
    outlet = Column(String)
    cashier = Column(String)
    datetime = Column(DateTime, nullable=False)
    smartshopper_last_four_digits = Column(String)
    total_items = Column(Integer)
    total_amount = Column(Integer)
    total_vat_incl_amount = Column(Integer)
    total_vat_amount = Column(Integer)
    total_zerorated_amount = Column(Integer)
    total_vitality_amount = Column(Integer)
    line_items = relationship("LineItem", backref="slip")
    media_item = relationship("MediaItem")
    __table_args__ = (UniqueConstraint('unique_id', name='unique_id_uc'), {'extend_existing': True})

class LineItem(Base):
    __tablename__ = 'line_items'
    id = Column(Integer, primary_key=True, index=True)
    slip_id = Column(Integer, ForeignKey('slips.id'))
    description = Column(String)
    quantity = Column(Integer)
    price = Column(Integer)
    total_price = Column(Integer)
    less_discount = Column(Integer)
    smartshopper_instant_savings = Column(Integer)
    is_zero_rated = Column(Boolean)
    is_vitality = Column(Boolean)
    __table_args__ = ({'extend_existing': True})