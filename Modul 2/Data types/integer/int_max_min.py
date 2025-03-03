# #- Практика:
#
#     <aside>
#     🍄
#
#     ### В папке `Data types` → В папке `integer` создайте файл `int_max_min.py`
#
#     ---
#
#     ### Описание темы: Максимум и минимум — функции `max()` и `min()`
#
#     Функции `max()` и `min()` позволяют находить наибольшее и наименьшее значение среди целых чисел. Эти функции полезны, когда нужно выбрать крайние значения из нескольких чисел.
#
#     Пример:
#
#     ```python
#     maximum = max(3, 5, 7)
#     minimum = min(3, 5, 7)
#     print(maximum)  # Выведет: 7
#     print(minimum)  # Выведет: 3
#
#     ```
#
#     ---
#
#     ### Задания:
#
#     ### **Задание #1**
#
#     - Создайте переменные `num1`, `num2`, и `num3` со значениями `10`, `20`, и `5` соответственно.
#     - Используйте функцию `max()` для нахождения наибольшего значения среди этих переменных и сохраните результат в переменную `max_value`.
#     - Выведите `max_value` на экран.

num1 = 10
num2 = 20
num3 = 5
max_value = max(num1, num2, num3)

print(max_value)


#     ### **Задание #2**
#
#     - Создайте переменные `a`, `b`, `c`, и `d` со значениями `15`, `23`, `42`, и `7`.
#     - Используйте функцию `min()` для нахождения наименьшего значения среди этих переменных и сохраните результат в переменную `min_value`.
#     - Выведите `min_value` на экран.

a = 15
b = 23
c = 42
d = 7
min_value = min(a, b, c, d)

print(min_value)




#     ### **Задание #3**
#
#     - Создайте список целых чисел `numbers = [3, 8, 1, 25, 19, 4, 7]`.
#     - Используйте функции `max()` и `min()` для нахождения максимального и минимального значения в списке `numbers`.
#     - Выведите результаты на экран.


numbers = [3 , 8 , 1 , 25, 19, 4 , 7]

print(max(numbers), min(numbers))

#     </aside>