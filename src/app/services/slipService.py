from io import BytesIO

import PyPDF2
from fastapi import Depends

import src.app.slips.models.database.models
from src.app.services.slipParser import SlipParser
from src.app.slips.daos import slipDAO
from src.app.slips.daos.slipDAO import SlipDAO
from src.app.slips.factories.slipFactory import SlipFactory
from src.app.slips.models.slip import DisplaySlip, Slip
from src.app.users.factories.userFactory import UserFactory
from fastapi_pagination import Page, Params

from src.app.users.models.database.models import User


class NoSlipFoundException(Exception):
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(self.detail)


class SlipService:
    def __init__(self, slip_factory: SlipFactory = Depends(SlipFactory), user_factory: UserFactory = Depends(UserFactory), slip_dao: SlipDAO = Depends(SlipDAO), slip_parser: SlipParser = Depends(SlipParser)):
        self.slip_parser = slip_parser
        self.slip_factory = slip_factory
        self.user_factory = user_factory
        self.slip_dao = slip_dao
        self.slip_parser = slip_parser

    def get_slip_by_id(self, slip_id: int) -> DisplaySlip:
        slip_entity = self.slip_dao.get_slip_by_id(slip_id)
        if slip_entity is None:
            raise NoSlipFoundException("No slip found with id: " + str(slip_id))

        return self.slip_factory.create_slip_from_slip_entity(slip_entity, slip_entity.line_items, slip_entity.user)

    def get_slip_by_unique_id(self, unique_id: str) -> DisplaySlip:
        slip_entity = self.slip_dao.get_slip_by_unique_id(unique_id)
        return self.slip_factory.create_slip_from_slip_entity(slip_entity, slip_entity.line_items, slip_entity.user)

    def get_slips_by_user_id(self, user_id: int,  params: Params = Params(page=1, size=100)) -> Page[DisplaySlip]:
        slips_response = []
        slips_page = self.slip_dao.get_slips_by_user_id(user_id, params)
        for slip_entity in slips_page.items:
            slips_response.append(self.slip_factory.create_slip_from_slip_entity(slip_entity, slip_entity.line_items, slip_entity.user))

        return Page.create(items=slips_response, params=params, total=slips_page.total)

    def get_all_slips(self, params: Params = Params(page=1, size=100)) -> Page[DisplaySlip]:
        slips_response = []
        slips_page = self.slip_dao.get_all_slips(params)
        for slip_entity in slips_page.items:
            slips_response.append(self.slip_factory.create_slip_from_slip_entity(slip_entity, slip_entity.line_items, slip_entity.user))

        return Page.create(items=slips_response, params=params, total=slips_page.total)


    def create_slip_from_file(self, file_stream: BytesIO, file_name: str, user: User) -> DisplaySlip:
        pdfReader = PyPDF2.PdfReader(stream=file_stream, strict=False, password=None)
        text = ""
        for page in pdfReader.pages:
            text += page.extract_text()

        slip = self.slip_parser.parse_slip_text_to_obtain_slip(text, user, file_name)
        slip_entity: src.app.slips.models.database.models.Slip = self.slip_factory.create_slip_entity_from_slip(slip)
        existing_slip_entity: src.app.slips.models.database.models.Slip = self.slip_dao.get_slip_by_unique_id(slip.unique_id)
        if existing_slip_entity is not None:
            # update instead of create
            slip_entity = self.slip_dao.update_slip(existing_slip_entity.id, slip_entity)
            #delete all existing line items belonging to this slip, they will be readded later
            self.slip_dao.delete_line_items(existing_slip_entity)
        else:
            slip_entity = self.slip_dao.create_slip(slip_entity)

        line_items = self.slip_parser.parse_slip_text_to_obtain_line_items(text, slip_entity)
        li_entities = self.slip_dao.create_line_items(line_items)
        li_models = self.slip_factory.create_line_items_from_line_item_entities(li_entities)
        return self.slip_factory.create_slip_from_slip_entity(slip_entity, li_models, user)

    def create_slip(self, slip: Slip) -> DisplaySlip:
        slip_entity = self.slip_factory.create_slip_entity_from_slip(slip)
        slip_entity = self.slip_dao.create_slip(slip_entity)

        return self.slip_factory.create_slip_from_slip_entity(slip_entity)

    def get_slips_by_month(self, month, year, user_id, params):
        slips_response = []
        slips_page = self.slip_dao.get_slips_by_month(month, year, user_id, params)
        for slip_entity in slips_page.items:
            slips_response.append(self.slip_factory.create_slip_from_slip_entity(slip_entity, slip_entity.line_items, slip_entity.user))

        return Page.create(items=slips_response, params=params, total=slips_page.total)

