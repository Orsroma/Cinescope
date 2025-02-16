import allure
import pytest
from Modul_4.Cinescope.utils.data_generator import DataGenerator


@allure.feature('Фильмы')
@allure.story('Создание фильма')
@allure.severity(allure.severity_level.CRITICAL)
@allure.testcase('https://testcase.manager/testcase/789', name='Тест-кейс')
@allure.title('Проверка создания фильма разными ролями')
@allure.description('Тест проверяет, какие роли могут создавать фильмы в системе Cinescope.')
@pytest.mark.parametrize("role, expected_status", [
    ("USER", 403),
    ("ADMIN", 403),
    ("SUPER_ADMIN", 201)
])
def test_create_movie_by_role(api_manager, user_create, role, expected_status, super_admin):
    """Проверяет, какие роли могут создавать фильмы"""

    with allure.step(f'Создание пользователя с ролью {role}'):
        user = user_create(role)
        assert "id" in user, f"Ошибка: в user_create нет ключа 'id', ответ: {user}"

    with allure.step('Генерация данных для фильма'):
        movie_data = {
            "name": DataGenerator.generate_funny_movie_title(),
            "price": 500,
            "description": "Фильм с элементами AQA и тестирования",
            "location": "MSK",
            "published": True,
            "genreId": 1
        }

    with allure.step(f'Проверка, что api_manager содержит movies_api'):
        assert hasattr(api_manager, "movies_api"), "Ошибка: у api_manager нет атрибута movies_api"

    with allure.step(f'Получение информации о пользователе {user["id"]}'):
        updated_user = api_manager.auth_api.get_user(user["id"], super_admin)
        assert role in updated_user["roles"], f"Ошибка: у пользователя нет роли {role} после обновления."

    with allure.step('Перелогиниваемся после смены роли'):
        new_token_response = api_manager.auth_api.login_user({"email": user["email"], "password": user["password"]})
        assert new_token_response.status_code == 201, (
            f"Ошибка: не удалось получить токен, статус {new_token_response.status_code}, ответ: {new_token_response.text}"
        )
        new_token_data = new_token_response.json()
        assert "accessToken" in new_token_data, f"Ошибка: В ответе нет accessToken: {new_token_data}"
        new_token = new_token_data["accessToken"]

    with allure.step('Формирование заголовков запроса'):
        headers = {
            "Authorization": f"Bearer {new_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    with allure.step('Отправка запроса на создание фильма'):
        response = api_manager.movies_api.create_movie(data=movie_data, headers=headers)
        assert response.status_code in [201, 403], (
            f"Ошибка: неожиданный статус-код {response.status_code}, ответ: {response.json()}"
        )

    with allure.step('Проверка ожидаемого статуса ответа'):
        assert response.status_code == expected_status, (
            f"Ожидали {expected_status}, но получили {response.status_code}. Данные: {response.json()}"
        )

    # @pytest.mark.parametrize("role, expected_status", [
    #     ("USER", 403),
    #     ("ADMIN", 200),
    #     ("SUPER_ADMIN", 200)
    # ])
    # def test_delete_movie_by_role(self, api_manager, user_create, role, expected_status):
    #     """Проверяет, какие роли могут удалять фильмы"""
    #     user = user_create(role)
    #
    #     # Если пользователь ADMIN или SUPER_ADMIN, создаем фильм перед удалением
    #     if role in ["ADMIN", "SUPER_ADMIN"]:
    #         movie_data = {
    #             "name": f"{role} Movie to Delete",
    #             "price": 100,
    #             "description": f"Фильм для удаления {role}",
    #             "location": "MSK",
    #             "published": True,
    #             "genreId": 1
    #         }
    #         create_response = api_manager.movies_api.create_movie(data=movie_data, token=user.token)
    #         assert create_response.status_code == 201, f"{role} должен создать фильм, но получил {create_response.status_code}"
    #         movie_id = create_response.json()["id"]
    #     else:
    #         movie_id = 1  # Для USER пытаемся удалить существующий фильм
    #
    #     response = api_manager.movies_api.delete_movie(movie_id=movie_id, token=user.token)
    #     assert response.status_code == expected_status, f"{role} должен получить {expected_status}, но получил {response.status_code}"
