from io import BytesIO
from typing import List

from fastapi import status, Depends, HTTPException, UploadFile
from fastapi_pagination import Page, Params

from ..models.slip import DisplaySlip, Slip
from ...services.slipService import SlipService, NoSlipFoundException
from ...users.models.user import User
from fastapi import APIRouter

from ...users.routers.login import get_current_user
from ...users.services.userService import UserService

router = APIRouter(tags=['Slips'])

@router.post('/slips', response_model=DisplaySlip)
async def create_slip(file: UploadFile,
                slip_service: SlipService = Depends(SlipService),
                current_user: User = Depends(get_current_user),
                user_service: UserService = Depends(UserService)):

    file_contents = await file.read()

    # Create a stream from the file contents
    file_stream: BytesIO = BytesIO(file_contents)
    return slip_service.create_slip_from_file(file_stream=file_stream, file_name=file.filename, user=user_service.get_user_by_name(current_user.username)
)


@router.get('/slips/bymonth', response_model=Page[DisplaySlip])
def get_slips_by_month(month: int, year: int, page: int = 1, page_size: int = 10, slip_service: SlipService = Depends(SlipService), current_user: User = Depends(get_current_user), user_service: UserService = Depends(UserService)):
    params: Params = Params(page=page, size=page_size)
    return slip_service.get_slips_by_month(month, year, user_service.get_user_by_name(current_user.username).id, params)


#add endpoint to get a slip by id
@router.get('/slips/{id}', response_model=DisplaySlip)
def get_slip(id: int, slip_service: SlipService = Depends(SlipService), current_user: User = Depends(get_current_user), user_service: UserService = Depends(UserService)):
    try:
        user = user_service.get_user_by_name(current_user.username)
        slip: DisplaySlip = slip_service.get_slip_by_id(id)
        if slip is not None:
            if slip.user.id == user.id:
                return slip
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to view this slip")
        return slip_service.get_slip_by_id(id, user)
    except NoSlipFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)

@router.get('/slips', response_model=Page[DisplaySlip])
def get_slips(page: int = 1, page_size:int = 10, slip_service: SlipService = Depends(SlipService), current_user: User = Depends(get_current_user), user_service: UserService = Depends(UserService)):
    params: Params = Params(page=page, size=page_size)
    return slip_service.get_slips_by_user_id(user_service.get_user_by_name(current_user.username).id, params)
