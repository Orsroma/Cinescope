import uuid

from faker import Faker
import pytest
import requests

from Modul_4.Cinescope.api.movies_api import MoviesAPI
from Modul_4.Cinescope.constants import BASE_URL, REGISTER_ENDPOINT, LOGIN_ENDPOINT
from Modul_4.Cinescope. custom_requester.custom_requester import CustomRequester
from Modul_4.Cinescope.entities.user import User
from Modul_4.Cinescope.enums.roles import Roles
from Modul_4.Cinescope.utils.data_generator import DataGenerator
from Modul_4.Cinescope.api.auth_api import AuthAPI
from Modul_4.Cinescope.api.api_manager import ApiManager
from Modul_4.Cinescope.utils.user_data import UserData
from Modul_4.Cinescope.models.base_models import TestUser


@pytest.fixture(scope="session")
def test_user() -> TestUser: # добавили формат возвращаеммого значения TestUser
    """
    Генерация случайного пользователя для тестов.
    """
    random_email = DataGenerator.generate_random_email()
    random_name = DataGenerator.generate_random_name()
    random_password = DataGenerator.generate_random_password()

    return TestUser( # возвращем обьект с опередленный набором полей и правил. нет возможности добавить чтото еще
        email=random_email,
        fullName=random_name,
        password=random_password,
        passwordRepeat=random_password, # field_validator автоматически проверит, что password и passwordRepeat совпадают
    ) # поле roles заполнится автоматически и бедт = [Role.USER]

@pytest.fixture(scope="session")
def registered_user(api_manager, test_user: TestUser):# указали тип TestUser для входящего значения test_user. теперь и интерпритатор 
                                                      # и разработчик понимают с чем они имеют дело
    """
    Фикстура для регистрации пользователя через auth_api.
    """
    response = api_manager.auth_api.register_user(test_user)
    response_data = response.json()
    test_user.id = response_data["id"]
    return test_user

@pytest.fixture
def super_admin(api_manager):
    """
    Фикстура для создания супер-администратора.
    """
    admin_data = {
        "email": "test-admin@mail.com",
        "password": "KcLMmxkJMjBD1",
        "passwordRepeat": "KcLMmxkJMjBD1"
    }
    login_response = api_manager.auth_api.login_user(admin_data)

    assert login_response.status_code in [200, 201], "Не удалось авторизоваться"

    access_token = login_response.json()["accessToken"]

    yield access_token  # Возвращаем токен для авторизации в тестах

@pytest.fixture(scope="session")
def super_admin_token(api_manager):
    """
    Получение токена для авторизации супер-админа.
    """
    login_data = {
        "email": "test-admin@mail.com",  # Убедитесь, что email супер-админа корректен
        "password": "KcLMmxkJMjBD1"      # Убедитесь, что пароль супер-админа корректен
    }
    response = api_manager.auth_api.login_user(login_data)
    assert response.status_code == 200, "Не удалось авторизоваться как супер-админ"
    return response.json()["accessToken"]

@pytest.fixture
def user_create(api_manager, super_admin):
    """Фикстура для создания пользователей с разными ролями."""
    created_users = []

    def _user_create(role: Roles):
        # ✅ Генерируем данные пользователя
        user_data = UserData.generate_user_data(role)
        email, password = user_data.email, user_data.password

        # ✅ Регистрируем пользователя
        response = api_manager.auth_api.register_user(user_data)

        if response.status_code == 201:
            user_id = response.json().get("id") or response.json().get("user", {}).get("id")
        elif response.status_code == 409:  # Пользователь уже существует
            login_response = api_manager.auth_api.login_user({"email": email, "password": password})
            assert login_response.status_code in [200, 201], "❌ Ошибка: не удалось авторизоваться"
            user_id = login_response.json()["user"]["id"]
        else:
            raise ValueError(f"❌ Ошибка: неожиданный статус {response.status_code} при регистрации")

        # ✅ Логинимся один раз, чтобы получить токен
        access_token = login_response.json()["accessToken"] if response.status_code == 409 else \
                       api_manager.auth_api.login_user({"email": email, "password": password}).json()["accessToken"]

        # ✅ Если роль не USER, обновляем через супер-админа
        if role != Roles.USER:
            api_manager.auth_api.change_user_role(user_id, [role.value], super_admin)

        created_users.append(user_id)  # ✅ Добавляем пользователя в список

        return {"id": user_id, "email": email,"password": user_data.password, "token": access_token}

    yield _user_create

    # ✅ Удаляем пользователей после тестов
    for user_id in created_users:
        try:
            api_manager.auth_api.delete_user(user_id, super_admin)
        except Exception as e:
            print(f"⚠️ Ошибка при удалении пользователя {user_id}: {e}")


@pytest.fixture(scope="session")
def api_manager():
    """Фикстура для создания экземпляра ApiManager"""
    print("⚡ Создаём ApiManager...")  # Добавляем отладку

    session = requests.Session()
    auth_requester = CustomRequester(session, "https://auth.dev-cinescope.coconutqa.ru/")
    movies_requester = CustomRequester(session, "https://api.dev-cinescope.coconutqa.ru/")

    api_manager_instance = ApiManager(auth_requester, movies_requester)

    # Проверяем, что объект создан правильно
    assert hasattr(api_manager_instance, "movies_api"), "Ошибка: у api_manager нет атрибута movies_api"
    assert hasattr(api_manager_instance, "auth_api"), "Ошибка: у api_manager нет атрибута auth_api"

    print("✅ ApiManager успешно создан!")  # Добавляем отладку
    return api_manager_instance


@pytest.fixture
def movie_data():
    """
    Генерация данных для создания фильма.
    """
    return {
        "name": "Test Movie",
        "price": 500,
        "description": "Описание тестового фильма",
        "location": "MSK",  # Исправлено значение location
        "published": True,
        "genreId": 1  # Исправлено значение genreId
    }


@pytest.fixture(scope="session")
def movies_api(requester):
    """
    Фикстура для MoviesAPI.
    """
    movies_base_url = "https://api.dev-cinescope.coconutqa.ru"
    return MoviesAPI(requester(movies_base_url), base_url=movies_base_url)

