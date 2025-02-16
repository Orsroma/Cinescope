from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum
import logging

#=============================================================================================================================================================
# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#=============================================================================================================================================================
# Простой пример (пункт "Зачем Pydantic в тестах?")

class User(BaseModel): # Создается класс User с помощью BaseModel от pydantic и указывается
    name: str       # что имя должно быть строкой
    age: int        # возраст должен быть числом
    adult: bool     # поле совершенолетие должно быть булевым значением

def get_user():  # функция get_user возвращает обьект dict с следущими полями
    return {
        "name": "Alice",
        "age": 25,
        "adult": "true"
    }

def test_user_data():
    user = User(**get_user())  # Проверяем возможность конвертации данных и соответствия типов данных с помощью Pydantic
    assert user.name == "Alice"  # Возможность дополнительных проверок 
    logger.info(f"{user.name=} {user.age=} {user.adult=}") # а также возможность удобного взаимодействия 

#=============================================================================================================================================================
#Пример на основе класса Product отображающий основные возможности:

class ProductType(str, Enum): 
    NEW = "new"
    PREVIOUS_USE = "previous_use"

class Manufacturer(BaseModel):
    name: str
    city: Optional[str] = None
    street: Optional[str] = None
    
class Product(BaseModel):
	# поле name может иметь длину в диапазоне от 3 до 50 символов и является строкой
    name: str = Field(..., min_length=3, max_length=50, description="Название продукта")
    # поле price должно быть больше 0
    price: float = Field(..., gt=0, description="Цена продукта")
    # поле in_stock принимает булево значение и установится по умолчанию = False
    in_stock: bool = Field(default=False, description="Есть ли в наличии")
    # поле colorдолжно быть строкой и принимает значение "black" по умолчанию
    color: str = "black"  
    # поле year не обязательное. можно не указывать при создании обьекта
    year: Optional[int] = None
    # поле product принимает тип Enum (может содержать только 1 из его значений)
    product: ProductType
    # поле manufacturer принимает тип другой BaseModel
    manufacturer: Manufacturer

def test_product():
    # Пример создания обьекта + в поле price передаём строку вместо числа
    product = Product(name="Laptop", price="999.99", product=ProductType.NEW, manufacturer=Manufacturer(name="MSI"))
    logger.info(f"{product=}")
    # Output: product=Product(name='Laptop', price=999.99, in_stock=False, color='black', year=None, product=<ProductType.NEW: 'new'>, manufacturer=Manufacturer(name='MSI', city=None, street=None))

    # Пример конвертации обьекта в json
    json_data = product.model_dump_json(exclude_unset=True)
    logger.info(f"{json_data=}")
    # Output: json_data='{"name":"Laptop","price":999.99,"product":"new","manufacturer":{"name":"MSI"}}'

    # Пример конвертации json в обьект
    new_product = Product.model_validate_json(json_data)
    logger.info(f"{new_product=}")
    # Output: new_product=Product(name='Laptop', price=999.99, in_stock=False, color='black', year=None, product=<ProductType.NEW: 'new'>, manufacturer=Manufacturer(name='MSI', city=None, street=None))


#=============================================================================================================================================================
#Поддержка кастомных валидаторов

from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import Optional

class PostgresClient(): #Mock - заглушка вмето реального сервиса. делающего запрос в базу данных
    @staticmethod
    def get(key: str):  #Всегда возвращает None
        return None

class Card(BaseModel):
    pan: str = Field(..., min_length=16, max_length=16, description="Номер карты")
    cvc: str = Field(...,  min_length=3, max_length=3)

    @field_validator("pan")  # кастомный валидатор для проверки поля pan
    def check_pan(cls, value: str) -> str:
        """
            не самый лучший пример. не стоит добавлять в валидаторы сложновесную логику
            но данным приером хочется показать что кастомные валидаторы лучше использовать 
            для ситуаций которые невозможно проверить доступной логикой Field
        """
        # Проверяем, существует ли карта в Redis
        if PostgresClient.get(f'card_by_pan_{value}') is None:
            raise ValueError("Такой карты не существует")
        return value

def test_field_validator():
# Попытка создать объект с данными. отсутствующими в базе данных
    try:
        card = Card(pan="1111222233334444", cvc="123")
        logger.info(card)
    except ValidationError as e:
        logger.info(f"Ошибка валидации: {e}")
        pass  # Ожидаем ошибку

#=============================================================================================================================================================
#Интеграция Pydantic с JSON Schema

from pydantic import BaseModel
import jsonschema

class User2(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool = True

def test_model_json_schema():
    # Генерируем JSON Schema
    user_schema = User2.model_json_schema()
    logger.info(user_schema)
    #Output:
    #{
    #    'properties':
    #    {
    #        'id':{'title': 'Id', 'type': 'integer'},
    #        'name':  {'title': 'Name', 'type': 'string'},
    #        'email': {'title': 'Email', 'type': 'string'}, 
    #        'is_active': {'default': True, 'title': 'Is Active', 'type': 'boolean'}
    #    },
    #    'required': ['id', 'name', 'email'],
    #    'title': 'User2', 'type': 'object'
    #}

    # Данные для валидации
    user2_data = {
        "id": 1,
        "name": "Alice",
        "email": "alice@example.com",
        "is_active": True
    }

    # Валидируем данные с использованием JSON Schema
    try:
        jsonschema.validate(user2_data, user_schema)
        logger.info("Данные валидны!")
    except jsonschema.ValidationError as e:
        logger.info("Ошибка валидации:", e)
        
#=============================================================================================================================================================

def test_bad_product_model():
    # Корректные данные
    product = Product(name="Laptop", price="999.99", product=ProductType.NEW, year=2005, manufacturer=Manufacturer(name="MSI"))
									
    assert isinstance(product, Product)
    assert product.name == "Laptop"
    assert product.price == 999.99
    assert product.product == ProductType.NEW
    assert product.year == 2005
    assert product.in_stock == False
    assert product.color == "black"

    # Неправильные данные (должна быть ошибка так как name должен быть длинее 3 символов)
    try:
        Product(name="x", price="999.99", product=ProductType.NEW, manufacturer=Manufacturer(name="MSI"))
    except ValueError:
        pass  # Ожидаем ошибку

#=============================================================================================================================================================


def main():# раскоментировав различные тесты в виде функций вы можете запустить и увидеть вывод в лог 
    logger.info("main")
    # logger.info("\n====================test_user_data====================\n")
    # test_user_data()
    # logger.info("\====================test_produc====================t\n")
    # test_product()
    # logger.info("\====================test_field_validator====================\n")
    # test_field_validator()
    # logger.info("\====================test_model_json_schema====================\n")
    # test_model_json_schema()
    # logger.info("\====================test_bad_product_model====================\n")
    # test_bad_product_model()

if __name__ == "__main__":
    main()
