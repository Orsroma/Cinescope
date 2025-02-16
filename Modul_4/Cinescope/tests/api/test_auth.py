
import datetime
import pytest
import requests
from Modul_4.Cinescope.constants import BASE_URL, HEADERS, REGISTER_ENDPOINT,  LOGIN_ENDPOINT
from Modul_4.Cinescope.custom_requester.custom_requester import CustomRequester
from Modul_4.Cinescope.api.api_manager import  ApiManager
from Modul_4.Cinescope.enums.roles import Roles
from Modul_4.Cinescope.models.base_models import RegisterUserResponse, TestUser

class TestAuthAPI:
    def test_register_user(self, api_manager: ApiManager, test_user: TestUser):
        """
        Тест на регистрацию пользователя.
        """
        response = api_manager.auth_api.register_user(test_user)

        register_user_response = RegisterUserResponse(**response.json())
        assert register_user_response.email ==  test_user.email, "Email не совпадает"