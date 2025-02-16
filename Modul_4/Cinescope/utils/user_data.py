from Modul_4.Cinescope.enums.roles import Roles
from Modul_4.Cinescope.models.base_models import TestUser
from Modul_4.Cinescope.utils.data_generator import DataGenerator

class UserData:
    @staticmethod
    def generate_user_data(role: Roles) -> TestUser:
        """Генерирует корректные данные пользователя с указанной ролью."""
        password = DataGenerator.generate_random_password()
        email = DataGenerator.generate_random_email()
        name = DataGenerator.generate_random_name()
        
        return TestUser(
            email = email,
            fullName = name,
            password = password,  # Сохраняем пароль
            passwordRepeat = password,  # Дублируем пароль
            verified = True,
            banned = False,
            roles = [role]  # Назначаем переданную роль
        )