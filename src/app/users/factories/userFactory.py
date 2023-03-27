from fastapi import Depends

from src.app.users.models.user import User, DisplayUser
from src.app.users.models.database import models

from src.app.users.services.passwordUtil import PasswordUtil

class UserFactory:
    def __init__(self, password_utils: PasswordUtil = Depends(PasswordUtil)):
        self.password_utils = password_utils
        pass

    def create_user_from_user_entity(self, user_entity: models.User) -> User:
        user_response = User(
            id=user_entity.id,
            first_name=user_entity.first_name,
            last_name=user_entity.last_name,
            email=user_entity.email,
            mobile_number=user_entity.mobile_number,
            password=user_entity.password
        )
        return user_response

    def create_display_user_from_user_entity(self, user_entity: models.User) -> DisplayUser:
        user_response = DisplayUser(
            id=user_entity.id,
            first_name=user_entity.first_name,
            last_name=user_entity.last_name,
            email=user_entity.email,
            mobile_number=user_entity.mobile_number,
            password=user_entity.password
        )
        return user_response

    def create_user_entity_from_user(self, user):
        password_hashed = self.password_utils.hash_pwd(user.password)
        new_user = models.User(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            mobile_number=user.mobile_number,
            password=password_hashed,
        )
        return new_user

