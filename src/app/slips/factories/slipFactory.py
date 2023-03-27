from datetime import datetime
import re

import datetime as datetime
from typing import List

from fastapi import Depends

from src.app.slips.models.database.models import LineItem
from src.app.users.factories.userFactory import UserFactory
from src.app.slips.models.slip import Slip, DisplaySlip, DisplayLineItem
from src.app.slips.models.database import models
from src.app.users.models.database import models as user_models


import sys

class SlipFactory:
    def __init__(self, user_factory: UserFactory = Depends(UserFactory)):
        self.user_factory = user_factory

    def create_slip_from_slip_entity(self, slip_entity: models.Slip, line_items: List[DisplayLineItem], user) -> DisplaySlip:
        slip_response = DisplaySlip(
            id=slip_entity.id,
            unique_id=slip_entity.unique_id,
            outlet=slip_entity.outlet,
            cashier=slip_entity.cashier,
            datetime=slip_entity.datetime,
            smartshopper_last_four_digits=slip_entity.smartshopper_last_four_digits,
            total_items=slip_entity.total_items,
            total_amount=slip_entity.total_amount,
            total_vat_incl_amount=slip_entity.total_vat_incl_amount,
            total_vat_amount=slip_entity.total_vat_amount,
            total_zerorated_amount=slip_entity.total_zerorated_amount,
            total_vitality_amount=slip_entity.total_vitality_amount,
            user=user,
            line_items=line_items
        )
        return slip_response

    def create_slip_entity_from_slip(self, slip: Slip) -> models.Slip:
        slip_entity = models.Slip(
            id=slip.id,
            unique_id=slip.unique_id,
            user_id=slip.user_id,
            outlet=slip.outlet,
            cashier=slip.cashier,
            datetime=slip.datetime,
            smartshopper_last_four_digits=slip.smartshopper_last_four_digits,
            total_items=slip.total_items,
            total_amount=slip.total_amount,
            total_vat_incl_amount=slip.total_vat_incl_amount,
            total_vat_amount=slip.total_vat_amount,
            total_zerorated_amount=slip.total_zerorated_amount,
            total_vitality_amount=slip.total_vitality_amount,
        )
        return slip_entity

    def create_slip_from_text(self, text: str, user: user_models.User, file_name: str) -> Slip:
        #get unique id from filename. This the numeric value between PnPReceipt_ and _<date>.pdf
        unique_id = file_name.split("_")[1]
        #get outlet name from text. Its the second line in text
        outlet = text.splitlines()[1]
        #get cashier name from text. It;s the string after "Cashier: "
        cashier = text.split("CASHIER: ")[1].splitlines()[0]
        #get datetime from filename. It's the date after the last _ in the filename, It's formatted as "dd.mm.yy hh:mm" and needs to be converted to datetime
        dt = datetime.datetime.strptime(file_name.split("_")[2]+":"+file_name.split("_")[3].replace(".pdf",""), "%d.%m.%Y %H:%M")

        #read smartshopper last four digits from text. It's the 4 digits after "Smart Shopper card # ************"
        smartshopper_last_four_digits = text.split("Smart Shopper card #  ************")[1][:4]

        #get total items from text. It's the string after "Total Items: " and before the next space
        total_items = int(text.split("TOTAL ITEMS: ")[1].splitlines()[0].strip())

        #get total amount from text. It's the amount after "DUE VAT INCL"
        total_amount = text.split("DUE VAT INCL")[1].splitlines()[0].strip()
        total_amount = int(total_amount.replace(".","").replace(",",""))
        # get total included amount and total vat from a line in text in the following format "VAT INCL              1,037.59    135.34"
        # the total_vat_incl_amount is the first value in the line
        # thetotal_vat_amount is the second value in the line
        total_vat_incl_amount = text.split("VAT INCL")[2].splitlines()[0].split()[0]
        total_vat_incl_amount= int(total_vat_incl_amount.replace(".", "").replace(",",""))
        total_vat_amount = text.split("VAT INCL")[2].splitlines()[0].split()[1]
        total_vat_amount = int(total_vat_amount.replace(".", "").replace(",",""))

        total_zerorated_amount = text.split("# ZERO-RATED ")[1].splitlines()[0].split()[0]
        total_zerorated_amount = int(total_zerorated_amount.replace(".", "").replace(",",""))

        total_vitality_amount = SlipFactory.getTotalVitalityAmountInFile(text)
        slip = Slip(
            unique_id=unique_id,
            user_id=user.id,
            outlet=outlet,
            cashier=cashier,
            datetime=dt,
            smartshopper_last_four_digits=smartshopper_last_four_digits,
            total_items=total_items,
            total_amount=total_amount,
            total_vat_incl_amount=total_vat_incl_amount,
            total_vat_amount=total_vat_amount,
            total_zerorated_amount=total_zerorated_amount,
            total_vitality_amount=total_vitality_amount
        )
        return slip

    @staticmethod
    def find_vitality_amounts(text: str):
        # create a regex pattern
        pattern = r"\d+\.\d\dV|\d+\.\d\d#V"
        # create a regex object
        regex = re.compile(pattern)
        # find all matches
        matches = regex.findall(text)
        # return matches
        return matches

    @staticmethod
    def getTotalVitalityAmountInFile(text: str):
        vitality_amounts = SlipFactory.find_vitality_amounts(text)
        total_vitality_amount = 0;
        for amount in vitality_amounts:
            # strip non numeric endings from amount including a possible hash
            amount = amount[:-1]
            if amount[-1] == "#":
                amount = amount[:-1]
            total_vitality_amount += int(amount.replace(".","").replace(",",""))
        print(total_vitality_amount)
        return int(total_vitality_amount)

    def create_line_items_from_line_item_entities(self, li_entities) -> List[DisplayLineItem]:
        line_items = []
        for li_entity in li_entities:
            line_item = self.create_line_item_from_line_item_entity(li_entity)
            line_items.append(line_item)
        return line_items

    def create_line_item_from_line_item_entity(self, li_entity:LineItem) -> DisplayLineItem:
        display_line_item = DisplayLineItem(
            id=li_entity.id,
            slip_id=li_entity.slip_id,
            description=li_entity.description,
            quantity=li_entity.quantity,
            price=li_entity.price,
            total_price=li_entity.total_price,
            less_discount=li_entity.less_discount,
            smartshopper_instant_savings=li_entity.smartshopper_instant_savings,
            is_zero_rated=li_entity.is_zero_rated,
            is_vitality=li_entity.is_vitality
        )
        return display_line_item

    def create_line_item(self, quantity, description, price, total_price, less_discount, smartshopper_instant_savings, is_zero_rated, is_vitality, slip_entity) -> LineItem:
        line_item = LineItem(
            slip_id=slip_entity.id,
            quantity=quantity,
            description=description,
            price=price,
            total_price=total_price,
            less_discount=less_discount,
            smartshopper_instant_savings=smartshopper_instant_savings,
            is_zero_rated=is_zero_rated,
            is_vitality=is_vitality
        )
        return line_item
