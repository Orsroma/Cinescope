import pytest
from Modul_4.Cinescope.api.api_manager import ApiManager

class TestMoviesAPI:
    """
    Тесты для Movies API.
    """

    def test_get_all_movies(self, api_manager):
        """
        Тест для получения всех фильмов.
        """
        response = api_manager.movies_api.get_movies()
        assert response.status_code == 200, "Статус-код должен быть 200"
        assert "movies" in response.json(), "Ответ должен содержать ключ 'movies'"
        assert isinstance(response.json()["movies"], list), "'movies' должен быть списком"

    def test_get_movie_by_id(self, api_manager):
        """
        Тест для получения фильма по ID.
        """
        # Предположим, что фильм с ID '12345' существует
        movie_id = 50
        response = api_manager.movies_api.get_movie(movie_id)
        assert response.status_code == 200, "Статус-код должен быть 200"
        movie_data = response.json()
        assert movie_data.get("id") == movie_id, "ID фильма должен совпадать"
        assert "name" in movie_data, "Фильм должен содержать ключ 'name'"
        assert "price" in movie_data, "Фильм должен содержать ключ 'price'"

    def test_create_movie(self, api_manager, super_admin_token):
        """
        Тест для создания нового фильма.
        """
        movie_data = {
        "name": "Test Movie123",
        "price": 500,
        "description": "Описание тестового фильма",
        "location": "MSK",  # Исправлено значение location
        "published": True,
        "genreId": 1  # Исправлено значение genreId
        }
        response = api_manager.movies_api.create_movie(data=movie_data, token=super_admin_token)
        assert response.status_code == 201, "Фильм должен успешно создаться"
        created_movie = response.json()
        assert created_movie["name"] == movie_data["name"], "Имя фильма должно совпадать"
        assert created_movie["price"] == movie_data["price"], "Цена фильма должна совпадать"

    def test_delete_movie(self, api_manager, super_admin_token):
        """
        Тест для удаления фильма.
        """
        # Задайте заранее известный ID существующего фильма
        movie_id = 54  # Убедитесь, что этот фильм существует в базе данных

        # Удаляем фильм
        delete_response = api_manager.movies_api.delete_movie(movie_id=movie_id, token=super_admin_token)
        assert delete_response.status_code == 200, "Фильм должен успешно удалиться"

        # Проверяем, что фильм действительно удалён
        get_response = api_manager.movies_api.get_movie(movie_id=movie_id, expected_status=404)
        assert get_response.status_code == 404, "Фильм не должен существовать после удаления"