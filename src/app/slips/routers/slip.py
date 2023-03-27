from io import BytesIO

from fastapi import status, Depends, HTTPException, UploadFile

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


#add endpoint to get a slip by id
@router.get('/slips/{id}', response_model=DisplaySlip)
def get_slip(id: int, slip_service: SlipService = Depends(SlipService), current_user: User = Depends(get_current_user)):
    try:
        return slip_service.get_slip_by_id(id)
    except NoSlipFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)
