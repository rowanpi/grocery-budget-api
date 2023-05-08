from io import BytesIO

import PyPDF2
from fastapi import Depends, UploadFile

import src.app.slips.models.database.models
from src.app.media.services.mediaService import MediaService
from src.app.media.factories.mediaFactory import MediaFactory
from src.app.media.models.database import models as media_models
from src.app.slips.services.slipParser import SlipParser
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
    def __init__(self, slip_factory: SlipFactory = Depends(SlipFactory), user_factory: UserFactory = Depends(UserFactory), slip_dao: SlipDAO = Depends(SlipDAO), slip_parser: SlipParser = Depends(SlipParser), media_service: MediaService = Depends(MediaService), media_factory: MediaFactory = Depends(MediaFactory)):
        self.slip_parser = slip_parser
        self.slip_factory = slip_factory
        self.user_factory = user_factory
        self.slip_dao = slip_dao
        self.slip_parser = slip_parser
        self.media_service = media_service
        self.media_factory = media_factory

    def get_slip_by_id(self, slip_id: int) -> DisplaySlip:
        slip_entity = self.slip_dao.get_slip_by_id(slip_id)
        if slip_entity is None:
            raise NoSlipFoundException("No slip found with id: " + str(slip_id))
        view_media_item = None
        if slip_entity.media_item is not None:
            view_media_item = self.media_factory.create_media_item_from_media_item_entity(slip_entity.media_item)

        display_line_items = [self.slip_factory.create_line_item_from_line_item_entity(line_item) for line_item in
                              slip_entity.line_items]
        return self.slip_factory.create_slip_from_slip_entity(slip_entity, display_line_items, slip_entity.user, view_media_item)

    def get_slip_by_unique_id(self, unique_id: str) -> DisplaySlip:
        slip_entity = self.slip_dao.get_slip_by_unique_id(unique_id)
        if slip_entity is None:
            raise NoSlipFoundException("No slip found with unique_id: " + str(unique_id))
        view_media_item = None
        if slip_entity.media_item is not None:
            view_media_item = self.media_factory.create_media_item_from_media_item_entity(slip_entity.media_item)

        display_line_items = [self.slip_factory.create_line_item_from_line_item_entity(line_item) for line_item in
                              slip_entity.line_items]
        return self.slip_factory.create_slip_from_slip_entity(slip_entity, display_line_items, slip_entity.user, view_media_item)

    def get_slips_by_user_id(self, user_id: int,  params: Params = Params(page=1, size=100)) -> Page[DisplaySlip]:
        slips_response = []
        slips_page = self.slip_dao.get_slips_by_user_id(user_id, params)
        for slip_entity in slips_page.items:
            view_media_item = None
            if slip_entity.media_item is not None:
                view_media_item = self.media_factory.create_media_item_from_media_item_entity(slip_entity.media_item)
            display_line_items = [self.slip_factory.create_line_item_from_line_item_entity(line_item) for line_item in
                                  slip_entity.line_items]
            slips_response.append(self.slip_factory.create_slip_from_slip_entity(slip_entity, display_line_items, slip_entity.user, view_media_item))

        return Page.create(items=slips_response, params=params, total=slips_page.total)

    def get_all_slips(self, params: Params = Params(page=1, size=100)) -> Page[DisplaySlip]:
        slips_response = []
        slips_page = self.slip_dao.get_all_slips(params)
        for slip_entity in slips_page.items:
            view_media_item = None
            if slip_entity.media_item is not None:
                view_media_item = self.media_factory.create_media_item_from_media_item_entity(slip_entity.media_item)

            display_line_items = [self.slip_factory.create_line_item_from_line_item_entity(line_item) for line_item in
                                  slip_entity.line_items]
            slips_response.append(self.slip_factory.create_slip_from_slip_entity(slip_entity, display_line_items, view_media_item))

        return Page.create(items=slips_response, params=params, total=slips_page.total)


    async def create_slip_from_file(self, file: UploadFile, file_name: str, user: User) -> DisplaySlip:
        file_contents = await file.read()

        # Create a stream from the file contents
        file_stream: BytesIO = BytesIO(file_contents)

        pdfReader = PyPDF2.PdfReader(stream=file_stream, strict=False, password=None)
        text = ""
        for page in pdfReader.pages:
            text += page.extract_text()

        slip = self.slip_parser.parse_slip_text_to_obtain_slip(text, user, file_name)
        media_item: media_models.MediaItem = self.media_service.upload_media_item(file, file_name)
        slip.media_item_id = media_item.id
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
        view_media_item = self.media_factory.create_media_item_from_media_item_entity(media_item)
        return self.slip_factory.create_slip_from_slip_entity(slip_entity, li_models, user, view_media_item)

    def create_slip(self, slip: Slip) -> DisplaySlip:
        slip_entity = self.slip_factory.create_slip_entity_from_slip(slip)
        slip_entity = self.slip_dao.create_slip(slip_entity)

        return self.slip_factory.create_slip_from_slip_entity(slip_entity)

    def get_slips_by_month(self, month, year, user_id, params):
        slips_response = []
        slips_page = self.slip_dao.get_slips_by_month(month, year, user_id, params)
        for slip_entity in slips_page.items:
            view_media_item = None
            if slip_entity.media_item is not None:
                view_media_item = self.media_factory.create_media_item_from_media_item_entity(slip_entity.media_item)
            # convert slip_entity.line_items to list of DisplayLineItems
            display_line_items = [self.slip_factory.create_line_item_from_line_item_entity(line_item) for line_item in
                                  slip_entity.line_items]
            slips_response.append(self.slip_factory.create_slip_from_slip_entity(slip_entity, display_line_items, slip_entity.user, view_media_item))

        return Page.create(items=slips_response, params=params, total=slips_page.total)

    def get_slips_by_daterange(self, start_date, end_date, user_id, params):
        slips_response = []
        slips_page = self.slip_dao.get_slips_by_daterange(start_date, end_date, user_id, params)
        for slip_entity in slips_page.items:
            view_media_item = None
            if slip_entity.media_item is not None:
                view_media_item = self.media_factory.create_media_item_from_media_item_entity(slip_entity.media_item)
            # convert slip_entity.line_items to list of DisplayLineItems
            display_line_items = [self.slip_factory.create_line_item_from_line_item_entity(line_item) for line_item in
                                  slip_entity.line_items]
            slips_response.append(
                self.slip_factory.create_slip_from_slip_entity(slip_entity, display_line_items, slip_entity.user,
                                                               view_media_item))

        return Page.create(items=slips_response, params=params, total=slips_page.total)

