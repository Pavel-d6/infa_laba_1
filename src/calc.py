"""
Модуль калькулятора с использованием алгоритма Shunting Yard.
"""

import re
import operator
import const as constants

# Глобальный словарь операторов
OPERATORS = {
    "**": {
        "precedence": 4,
        "associativity": "right",
        "function": operator.pow,
    },
    "*": {
        "precedence": 3,
        "associativity": "left",
        "function": operator.mul,
    },
    "/": {
        "precedence": 3,
        "associativity": "left",
        "function": operator.truediv,
    },
    "//": {
        "precedence": 3,
        "associativity": "left",
        "function": operator.floordiv,
    },
    "%": {
        "precedence": 3,
        "associativity": "left",
        "function": operator.mod,
    },
    "+": {
        "precedence": 2,
        "associativity": "left",
        "function": operator.add,
    },
    "-": {
        "precedence": 2,
        "associativity": "left",
        "function": operator.sub,
    },
    "u+": {
        "precedence": 5,
        "associativity": "right",
        "function": lambda x: x,
    },
    "u-": {
        "precedence": 5,
        "associativity": "right",
        "function": lambda x: -x,
    },
}


class CalculatorError(Exception):
    """Базовый класс для ошибок калькулятора."""
    pass


class DivisionByZeroError(CalculatorError):
    """Ошибка деления на ноль."""
    pass


class InvalidExpressionError(CalculatorError):
    """Ошибка неверного выражения."""
    pass


def _is_number(token):
    """
    Проверяет, является ли токен числом.

    Args:
        token: Токен для проверки

    Returns:
        bool: True если токен является числом, иначе False
    """
    try:
        float(token)
        return True
    except ValueError:
        return False


def _process_unary_operators(tokens):
    """
    Обрабатывает унарные операторы + и -.

    Args:
        tokens: Список токенов

    Returns:
        List[str]: Список токенов с обработанными унарными операторами
    """
    processed_tokens = []

    for i, token in enumerate(tokens):
        if token in ["+", "-"]:
            is_unary = (
                i == 0
                or tokens[i - 1] == "("
                or (
                    tokens[i - 1] in OPERATORS
                    and not tokens[i - 1].startswith("u")
                )
            )

            if is_unary:
                processed_tokens.append(f"u{token}")
            else:
                processed_tokens.append(token)
        else:
            processed_tokens.append(token)

    return processed_tokens


def tokenize(expression):
    """
    Токенизация выражения.

    Args:
        expression: Строка с математическим выражением

    Returns:
        List[str]: Список токенов

    Raises:
        InvalidExpressionError: Если выражение содержит некорректные символы
    """
    tokens = re.findall(constants.TOKEN_PATTERN, expression, re.VERBOSE)
    tokens = [token.strip() for token in tokens if token.strip()]

    for token in tokens:
        if not (
            _is_number(token)
            or token in OPERATORS
            or token in "()"
            or token in ["**", "//"]
            or token.startswith("u")
        ):
            raise InvalidExpressionError(
                constants.ERROR_INVALID_SYMBOL.format(symbol=token)
            )

    return _process_unary_operators(tokens)


def _should_pop_operator(stack_top, current_token):
    """
    Определяет, нужно ли выталкивать оператор из стека.

    Args:
        stack_top: Верхний элемент стека
        current_token: Текущий токен-оператор

    Returns:
        bool: True если нужно вытолкнуть, иначе False
    """
    if stack_top not in OPERATORS:
        return False

    stack_op = OPERATORS[stack_top]
    current_op = OPERATORS[current_token]

    if stack_op["precedence"] > current_op["precedence"]:
        return True

    if (
        stack_op["precedence"] == current_op["precedence"]
        and current_op["associativity"] == "left"
    ):
        return True

    return False


def to_rpn(tokens):
    """
    Преобразует инфиксное выражение в обратную польскую запись (RPN).

    Args:
        tokens: Список токенов в инфиксной записи

    Returns:
        List[str]: Список токенов в RPN

    Raises:
        InvalidExpressionError: Если скобки несогласованы
    """
    output = []
    operator_stack = []

    for token in tokens:
        if _is_number(token):
            output.append(token)

        elif token in OPERATORS:
            while (
                operator_stack
                and operator_stack[-1] != "("
                and _should_pop_operator(operator_stack[-1], token)
            ):
                output.append(operator_stack.pop())

            operator_stack.append(token)

        elif token == "(":
            operator_stack.append(token)

        elif token == ")":
            while operator_stack and operator_stack[-1] != "(":
                output.append(operator_stack.pop())

            if not operator_stack:
                raise InvalidExpressionError(constants.ERROR_UNBALANCED_PARENTHESES)

            operator_stack.pop()  # Удаляем '('

    while operator_stack:
        if operator_stack[-1] == "(":
            raise InvalidExpressionError(constants.ERROR_UNBALANCED_PARENTHESES)
        output.append(operator_stack.pop())

    return output


def _validate_operation(operator, left, right):
    """
    Проверяет корректность операции.

    Args:
        operator: Оператор
        left: Левый операнд
        right: Правый операнд

    Raises:
        DivisionByZeroError: При делении на ноль
        InvalidExpressionError: При некорректной операции для типов
    """
    if operator in ["/", "//", "%"] and right == 0:
        raise DivisionByZeroError(constants.ERROR_DIVISION_BY_ZERO)

    if operator in ["//", "%"]:
        if not isinstance(left, int) or not isinstance(right, int):
            raise InvalidExpressionError(
                constants.ERROR_INTEGER_OPERATION.format(operator=operator)
            )


def evaluate_rpn(rpn_tokens):
    """
    Вычисляет значение выражения в RPN.

    Args:
        rpn_tokens: Список токенов в RPN

    Returns:
        Union[int, float]: Результат вычисления

    Raises:
        InvalidExpressionError: Если выражение некорректно
        DivisionByZeroError: При делении на ноль
    """
    stack = []

    for token in rpn_tokens:
        if _is_number(token):
            if "." in token:
                stack.append(float(token))
            else:
                stack.append(int(token))

        elif token in OPERATORS:
            if token.startswith("u"):
                if len(stack) < 1:
                    raise InvalidExpressionError(constants.ERROR_NOT_ENOUGH_OPERANDS)

                operand = stack.pop()
                result = OPERATORS[token]["function"](operand)
                stack.append(result)

            else:
                if len(stack) < 2:
                    raise InvalidExpressionError(constants.ERROR_NOT_ENOUGH_OPERANDS)

                right = stack.pop()
                left = stack.pop()

                _validate_operation(token, left, right)

                result = OPERATORS[token]["function"](left, right)
                stack.append(result)

    if len(stack) != 1:
        raise InvalidExpressionError(constants.ERROR_INVALID_EXPRESSION)

    return stack[0]


def _check_parentheses(expression):
    """
    Проверяет сбалансированность скобок.

    Args:
        expression: Выражение для проверки

    Returns:
        bool: True если скобки сбалансированы, иначе False
    """
    stack = []
    for char in expression:
        if char == "(":
            stack.append(char)
        elif char == ")":
            if not stack:
                return False
            stack.pop()
    return len(stack) == 0


def calculate(expression):
    """
    Основная функция вычисления выражения.

    Args:
        expression: Строка с математическим выражением

    Returns:
        Union[int, float]: Результат вычисления

    Raises:
        CalculatorError: При ошибках вычисления
    """
    try:
        expression = expression.replace(" ", "")

        if not expression:
            raise InvalidExpressionError(constants.ERROR_EMPTY_EXPRESSION)

        if not _check_parentheses(expression):
            raise InvalidExpressionError(constants.ERROR_UNBALANCED_PARENTHESES)

        tokens = tokenize(expression)
        rpn_tokens = to_rpn(tokens)
        result = evaluate_rpn(rpn_tokens)

        return result

    except CalculatorError:
        raise
    except Exception as e:
        raise CalculatorError(constants.ERROR_UNKNOWN.format(error=e))


def calculate_expression(expression):
    """
    Упрощенная функция для вычисления выражения.

    Args:
        expression: Строка с математическим выражением

    Returns:
        Union[int, float]: Результат вычисления
    """
    return calculate(expression)