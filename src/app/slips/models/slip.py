from pydantic import BaseModel, EmailStr, Field, BaseConfig
import datetime

from src.app.users.models.user import DisplayUser

BaseConfig.arbitrary_types_allowed = True

class Slip(BaseModel):
    id: int = Field(None)
    user_id: int = Field(None)
    unique_id: str = Field(None)
    outlet: str = Field(None)
    cashier: str = Field(None)
    datetime: datetime.datetime
    smartshopper_last_four_digits: str = Field(None)
    total_items: int = Field(None)
    total_amount: int = Field(None)
    total_vat_incl_amount: int = Field(None)
    total_vat_amount: int = Field(None)
    total_zerorated_amount: int = Field(None)
    total_vitality_amount: int = Field(None)
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "unique_id": "123456789",
                "outlet": "Pick n Pay",
                "cashier": "John Smith",
                "datetime": "2021-01-01 12:00:00",
                "smartshopper_last_four_digits": "1234",
                "total_items": 10,
                "total_amount": 100000, # 1000.00
                "total_vat_incl_amount": 100000, # 1000.00
                "total_vat_amount": 10000, # 100.00
                "total_zerorated_amount": 0, # 0.00
                "total_vitality_amount": 0 # 0.00
            }
        }


class DisplaySlip(BaseModel):
    id: int = Field(None)
    unique_id: str = Field(None)
    outlet: str = Field(None)
    cashier: str = Field(None)
    datetime: datetime.datetime
    smartshopper_last_four_digits: str = Field(None)
    total_items: int = Field(None)
    total_amount: int = Field(None)
    total_vat_incl_amount: int = Field(None)
    total_vat_amount: int = Field(None)
    total_zerorated_amount: int = Field(None)
    total_vitality_amount: int = Field(None)
    user: DisplayUser = Field(None)
    line_items: list = Field(None)
    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "unique_id": "123456789",
                "outlet": "Pick n Pay",
                "cashier": "John Smith",
                "datetime": "2021-01-01 12:00:00",
                "smartshopper_last_four_digits": "1234",
                "total_items": 10,
                "total_amount": 100000, # 1000.00
                "total_vat_incl_amount": 100000, # 1000.00
                "total_vat_amount": 10000, # 100.00
                "total_zerorated_amount": 0, # 0.00
                "total_vitality_amount": 0, # 0.00
                "user": {
                    "id": 1,
                    "first_name": "Joe",
                    "last_name": "Bloggs",
                    "email": "test@email.com"
                }
            }
        }


class DisplayLineItem(BaseModel):
    id: int = Field(None)
    slip_id: int = Field(None)
    quantity: int = Field(None)
    description: str = Field(None)
    price: int = Field(None)
    total_price: int = Field(None)
    less_discount: int = Field(None)
    smartshopper_instant_savings: int = Field(None)
    is_zero_rated: bool = Field(None)
    is_vitality: bool = Field(None)
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "slip_id": 1,
                "quantity": 1,
                "description": "Bread",
                "price": 10000, # 100.00
                "total_price": 10000, # 100.00
                "less_discount": 0, # 0.00
                "smartshopper_instant_savings": 0, # 0.00
                "is_zero_rated": False,
                "is_vitality": False
            }
        }

