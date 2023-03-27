from typing import List

from fastapi import Depends

from src.app.slips.factories.slipFactory import SlipFactory
from src.app.slips.models.database.models import LineItem
from src.app.slips.models.slip import Slip
import re

from src.app.users.models.database.models import User


class SlipParser:
    def __init__(self, slip_factory: SlipFactory = Depends(SlipFactory)):
        self.slip_factory = slip_factory


    def parse_slip_text_to_obtain_slip(self, text: str, user: User, file_name: str) -> Slip:
        # create pdfReader

        return self.slip_factory.create_slip_from_text(text, user, file_name)


    def parse_slip_text_to_obtain_line_items(self, text: str, slip_entity: Slip) -> List[LineItem]:
        pattern = r'   [0-9,]+.[0-9]{2}(#)?(V)?(#V)?'
        clean_text_pattern = r'Page [0-9]+/[0-9]+'
        clean_text = re.sub(clean_text_pattern, '', text)
        lineItems: List[LineItem] = []
        #split text into lines
        lines: List[str] = clean_text.splitlines()
        # find the line that starts with CASHIER: and skip over everything before and including that line
        line_number = 0
        while not lines[line_number].startswith("CASHIER:"):
            line_number += 1
        line_number += 1

        while line_number <= len(lines):
            #check if we at the end of the line items
            if "DUE VAT INCL" in lines[line_number]:
                break
                #end of line items
            #check if line has a numeric value with 2 decimal places
            if re.search(pattern, lines[line_number]):
                #remove the amount with 2 decimal places from the line
                description = re.sub(pattern, "", lines[line_number]).strip()
                total_price_str = lines[line_number].replace(description, "").strip()
                is_zero_rated = "#" in total_price_str
                is_vitality = "V" in total_price_str
                total_price = int(total_price_str.replace(",", "").replace(".", "").replace("#", "").replace("V", ""))
                #check if there is a discount in the next line
                less_discount = 0
                smartshopper_instant_savings = 0
                if(line_number + 1 < len(lines)):
                    if "** Less cash-off" in lines[line_number + 1]:
                        line_number = line_number + 1
                        #remove the amount with 2 decimal places from the line
                        discount_str = lines[line_number].replace("** Less cash-off", "").strip().replace("-", "") # we only care about the amount not the sign
                        less_discount = int(discount_str.replace(",", "").replace(".", ""))
                    elif "Smart Shopper Instant Saving" in lines[line_number + 1]:
                        line_number = line_number + 1
                        #remove the amount with 2 decimal places from the line
                        smartshopper_instant_savings_str = lines[line_number].replace("Smart Shopper Instant Saving", "").strip().replace("-", "") # we only care about the amount not the sign
                        smartshopper_instant_savings = int(smartshopper_instant_savings_str.replace(",", "").replace(".", ""))

                #here price is the total price of the item since there is 1 item.
                line_item = self.slip_factory.create_line_item(1, description, total_price, total_price, less_discount, smartshopper_instant_savings, is_zero_rated, is_vitality, slip_entity)
                lineItems.append(line_item)
                line_number = line_number + 1
            elif "Price Reduced" in lines[line_number].strip() and "Smart Shopper Instant Savings" in lines[line_number].strip():
                line_number = line_number + 1
                #remove the amount with 2 decimal places from the line
                description = re.sub(pattern, "", lines[line_number]).strip()
                total_price_str = lines[line_number].replace(description, "").strip()
                is_zero_rated = "#" in total_price_str
                is_vitality = "V" in total_price_str
                # here we get the total price from the Was price in the following line
                total_price = int(total_price_str.replace(",", "").replace(".", "").replace("#", "").replace("V", ""))
                #check if there is a discount in the next line
                was_amount = 0
                smartshopper_instant_savings = 0
                line_item = None
                if lines[line_number + 1].startswith("Was   ") and "Reduced by" in lines[line_number + 1]:
                    line_number = line_number + 1
                    # remove the amount with 2 decimal places from the line
                    was_and_reduced_by = lines[line_number].replace("Was", "").strip()
                    was_and_reduced_by = was_and_reduced_by.replace("Reduced by", "").strip()
                    was_and_reduced_by_amounts = was_and_reduced_by.split("-")
                    was_amount = int(was_and_reduced_by_amounts[0].replace(",", "").replace(".", "").strip())
                    reduced_by_amount = int(was_and_reduced_by_amounts[1].replace(",", "").replace(".", "").strip())

                #here price is the total price of the item since there is 1 item.
                    line_item = self.slip_factory.create_line_item(1, description, was_amount, was_amount, 0, reduced_by_amount, is_zero_rated, is_vitality, slip_entity)
                else:
                    #this is added here just for safety
                    line_item = self.slip_factory.create_line_item(1, description, total_price, total_price, 0, 0, is_zero_rated, is_vitality, slip_entity)

                lineItems.append(line_item)
                line_number = line_number + 1
            else: #line doesnt have a numeric value because more than 1 item was bought and the details are in the second line
                description = lines[line_number].strip()
                line_number = line_number + 1
                #split line by @
                line_parts = lines[line_number].split("@")
                quantity_str = line_parts[0].strip()
                quantity = int(quantity_str)
                price_and_total = line_parts[1].strip()
                # separate the price and total which is separate by an undefined amount of whitespace
                price_and_total_parts = price_and_total.split()
                price = int(price_and_total_parts[0].replace(",", "").replace(".", ""))
                total_price_str = price_and_total_parts[1]
                is_zero_rated = "#" in total_price_str
                is_vitality = "V" in total_price_str
                total_price = int(total_price_str.replace(",", "").replace(".", "").replace("#", "").replace("V", ""))
                #check if there is a discount in the next line
                less_discount = 0
                smartshopper_instant_savings = 0
                if (line_number + 1 < len(lines)):
                    if "** Less cash-off" in lines[line_number + 1]:
                        line_number = line_number + 1
                        # remove the amount with 2 decimal places from the line
                        discount_str = lines[line_number].replace("** Less cash-off", "").strip().replace("-",
                                                                                                          "")  # we only care about the amount not the sign
                        less_discount = int(discount_str.replace(",", "").replace(".", ""))
                    elif "Smart Shopper Instant Saving" in lines[line_number + 1]:
                        line_number = line_number + 1
                        #remove the amount with 2 decimal places from the line
                        smartshopper_instant_savings_str = lines[line_number].replace("Smart Shopper Instant Saving", "").strip().replace("-", "") # we only care about the amount not the sign
                        smartshopper_instant_savings = int(smartshopper_instant_savings_str.replace(",", "").replace(".", ""))

                line_item = self.slip_factory.create_line_item(quantity, description, price, total_price, less_discount, smartshopper_instant_savings, is_zero_rated, is_vitality, slip_entity)
                lineItems.append(line_item)
                line_number = line_number + 1


        return lineItems