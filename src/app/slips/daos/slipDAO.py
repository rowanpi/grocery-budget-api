from fastapi import Depends

from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import Page, Params

from src.app.database import get_db, SessionLocal
from src.app.slips.models.database import models


class SlipDAO:
    def __init__(self, db: SessionLocal = Depends(get_db)):
        self.db = db

    def get_all_slips(self,  params: Params = Params(page=1, size=100)) -> Page[models.Slip]:
        return paginate(self.db.query(models.Slip), params)

    def get_slip_by_id(self, slip_id: int) -> models.Slip:
        return self.db.query(models.Slip).filter(models.Slip.id == slip_id).first()

    def get_slip_by_unique_id(self, unique_id: str) -> models.Slip:
        return self.db.query(models.Slip).filter(models.Slip.unique_id == unique_id).first()

    def get_slips_by_user_id(self, user_id: int, params: Params = Params(page=1, size=100)) -> Page[models.Slip]:
        return paginate(self.db.query(models.Slip).filter(models.Slip.user_id == user_id), params)

    def create_slip(self, slip: models.Slip) -> models.Slip:
        self.db.add(slip)
        self.db.commit()
        self.db.refresh(slip)
        return slip

    def update_slip(self, existing_slip_id: id, slip: models.Slip) -> models.Slip:
        #update existing slip database row with new slip data in slip
        existing_slip: models.Slip = self.db.query(models.Slip).filter(models.Slip.id == existing_slip_id).first()
        existing_slip.unique_id = slip.unique_id
        existing_slip.outlet = slip.outlet
        existing_slip.cashier = slip.cashier
        existing_slip.datetime = slip.datetime
        existing_slip.smartshopper_last_four_digits = slip.smartshopper_last_four_digits
        existing_slip.total_items = slip.total_items
        existing_slip.total_amount = slip.total_amount
        existing_slip.total_vat_incl_amount = slip.total_vat_incl_amount
        existing_slip.total_vat_amount = slip.total_vat_amount
        existing_slip.total_zerorated_amount = slip.total_zerorated_amount
        existing_slip.total_vitality_amount = slip.total_vitality_amount
        existing_slip.user_id = slip.user_id
        self.db.commit()
        self.db.refresh(existing_slip)
        return existing_slip

    def remove_slip(self, slip: models.Slip) -> models.Slip:
        self.db.delete(slip)
        self.db.commit()
        return slip

    def create_line_items(self, line_items):
        self.db.add_all(line_items)
        self.db.commit()
        return line_items

    def delete_line_items(self, slip: models.Slip):
        #delete all line items relating to this slip
        self.db.query(models.LineItem).filter(models.LineItem.slip_id == slip.id).delete()

