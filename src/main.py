"""
Точка входа в приложение калькулятора.
"""

import const as constants
import calc


def main():
    """
    Основная функция для запуска калькулятора в интерактивном режиме.
    """
    print(constants.WELCOME_MESSAGE)

    while True:
        try:
            expression = input("\nВведите выражение: ").strip()

            if expression.lower() in constants.EXIT_COMMANDS:
                print("До свидания!")
                break

            if not expression:
                continue

            result = calc.calculate(expression)
            print(f"Результат: {result}")

        except (
            calc.InvalidExpressionError,
            calc.DivisionByZeroError,
            calc.CalculatorError,
        ) as e:
            print(f"Ошибка: {e}")
        except Exception as e:
            print(f" {constants.ERROR_UNKNOWN.format(error=e)}")


if __name__ == "__main__":
    main()