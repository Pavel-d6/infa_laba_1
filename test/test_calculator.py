"""
Тесты для калькулятора с использованием pytest.
"""

import sys
import os

# Добавляем путь к папке src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pytest
from calc import (
    calculate,
    tokenize,
    to_rpn,
    evaluate_rpn,
    InvalidExpressionError,
    DivisionByZeroError,
    CalculatorError,
)


class TestTokenize:
    """Тесты для функции tokenize."""

    def test_basic_tokens(self):
        """Тест базовых токенов."""
        assert tokenize("2 + 2") == ["2", "+", "2"]
        assert tokenize("3 * 4 - 5") == ["3", "*", "4", "-", "5"]
        assert tokenize("10 / 2") == ["10", "/", "2"]

    def test_numbers(self):
        """Тест различных форматов чисел."""
        assert tokenize("123") == ["123"]
        assert tokenize("12.34") == ["12.34"]
        assert tokenize("0.5") == ["0.5"]
        assert tokenize("-5.5") == ["u-", "5.5"]

    def test_unary_operators(self):
        """Тест унарных операторов."""
        assert tokenize("-5") == ["u-", "5"]
        assert tokenize("+3") == ["u+", "3"]
        assert tokenize("2 + -3") == ["2", "+", "u-", "3"]
        assert tokenize("2 - +3") == ["2", "-", "u+", "3"]
        assert tokenize("(-2)") == ["(", "u-", "2", ")"]
        assert tokenize("-(2 + 3)") == ["u-", "(", "2", "+", "3", ")"]

    def test_complex_operators(self):
        """Тест сложных операторов."""
        assert tokenize("2 ** 3") == ["2", "**", "3"]
        assert tokenize("10 // 3") == ["10", "//", "3"]
        assert tokenize("10 % 3") == ["10", "%", "3"]

    def test_parentheses(self):
        """Тест скобок."""
        assert tokenize("(2 + 3)") == ["(", "2", "+", "3", ")"]
        assert tokenize("((2 + 3) * 4)") == ["(", "(", "2", "+", "3", ")", "*", "4", ")"]

    def test_invalid_symbols(self):
        """Тест некорректных символов."""
        with pytest.raises(InvalidExpressionError):
            tokenize("2 @ 3")
        with pytest.raises(InvalidExpressionError):
            tokenize("abc + 3")
        with pytest.raises(InvalidExpressionError):
            tokenize("2 $ 3")


class TestToRPN:
    """Тесты для функции to_rpn."""

    def test_basic_expressions(self):
        """Тест базовых выражений."""
        assert to_rpn(["2", "+", "2"]) == ["2", "2", "+"]
        assert to_rpn(["3", "*", "4"]) == ["3", "4", "*"]
        assert to_rpn(["2", "+", "3", "*", "4"]) == ["2", "3", "4", "*", "+"]
        assert to_rpn(["(", "2", "+", "3", ")", "*", "4"]) == ["2", "3", "+", "4", "*"]

    def test_operator_precedence(self):
        """Тест приоритета операторов."""
        assert to_rpn(["2", "+", "3", "*", "4"]) == ["2", "3", "4", "*", "+"]
        assert to_rpn(["2", "*", "3", "+", "4"]) == ["2", "3", "*", "4", "+"]
        assert to_rpn(["2", "**", "3", "**", "2"]) == ["2", "3", "2", "**", "**"]

    def test_unary_operators_rpn(self):
        """Тест унарных операторов в RPN."""
        assert to_rpn(["u-", "5"]) == ["5", "u-"]
        assert to_rpn(["u+", "3"]) == ["3", "u+"]
        assert to_rpn(["2", "+", "u-", "3"]) == ["2", "3", "u-", "+"]

    def test_parentheses_errors(self):
        """Тест ошибок скобок."""
        with pytest.raises(InvalidExpressionError):
            to_rpn(["(", "2", "+", "3"])
        with pytest.raises(InvalidExpressionError):
            to_rpn(["2", "+", "3", ")"])


class TestEvaluateRPN:
    """Тесты для функции evaluate_rpn."""

    def test_basic_operations(self):
        """Тест базовых операций."""
        assert evaluate_rpn(["2", "2", "+"]) == 4
        assert evaluate_rpn(["5", "3", "-"]) == 2
        assert evaluate_rpn(["4", "2", "*"]) == 8
        assert evaluate_rpn(["10", "2", "/"]) == 5.0

    def test_complex_operations(self):
        """Тест сложных операций."""
        assert evaluate_rpn(["2", "3", "**"]) == 8
        assert evaluate_rpn(["10", "3", "//"]) == 3
        assert evaluate_rpn(["10", "3", "%"]) == 1

    def test_unary_operations(self):
        """Тест унарных операций."""
        assert evaluate_rpn(["5", "u-"]) == -5
        assert evaluate_rpn(["3", "u+"]) == 3
        assert evaluate_rpn(["2", "3", "u-", "+"]) == -1

    def test_float_operations(self):
        """Тест операций с дробными числами."""
        assert evaluate_rpn(["2.5", "2", "*"]) == 5.0
        assert evaluate_rpn(["5.5", "2.5", "+"]) == 8.0
        assert evaluate_rpn(["10.0", "4.0", "/"]) == 2.5

    def test_division_by_zero(self):
        """Тест деления на ноль."""
        with pytest.raises(DivisionByZeroError):
            evaluate_rpn(["5", "0", "/"])
        with pytest.raises(DivisionByZeroError):
            evaluate_rpn(["10", "0", "//"])
        with pytest.raises(DivisionByZeroError):
            evaluate_rpn(["5", "0", "%"])

    def test_integer_operations(self):
        """Тест операций только для целых чисел."""
        assert evaluate_rpn(["10", "3", "//"]) == 3
        assert evaluate_rpn(["10", "3", "%"]) == 1
        
        with pytest.raises(InvalidExpressionError):
            evaluate_rpn(["10.5", "3", "//"])
        with pytest.raises(InvalidExpressionError):
            evaluate_rpn(["10", "3.5", "%"])

    def test_not_enough_operands(self):
        """Тест недостатка операндов."""
        with pytest.raises(InvalidExpressionError):
            evaluate_rpn(["2", "+"])
        with pytest.raises(InvalidExpressionError):
            evaluate_rpn(["+"])


class TestCalculate:
    """Тесты для основной функции calculate."""

    def test_simple_expressions(self):
        """Тест простых выражений."""
        assert calculate("2 + 2") == 4
        assert calculate("10 - 5") == 5
        assert calculate("3 * 4") == 12
        assert calculate("15 / 3") == 5.0

    def test_complex_expressions(self):
        """Тест сложных выражений."""
        assert calculate("2 + 3 * 4") == 14
        assert calculate("(2 + 3) * 4") == 20
        assert calculate("2 ** 3 ** 2") == 512
        assert calculate("10 // 3 + 10 % 3") == 4

    def test_expressions_with_spaces(self):
        """Тест выражений с пробелами."""
        assert calculate("  2 + 2  ") == 4
        assert calculate("2+2") == 4
        assert calculate(" ( 2 + 3 ) * 4 ") == 20

    def test_unary_operators_calculation(self):
        """Тест вычислений с унарными операторами."""
        assert calculate("-5") == -5
        assert calculate("+3") == 3
        assert calculate("2 + -3") == -1
        assert calculate("-(2 + 3)") == -5
        assert calculate("-2 * -3") == 6

    def test_float_calculations(self):
        """Тест вычислений с дробными числами."""
        assert calculate("2.5 * 2") == 5.0
        assert calculate("0.1 + 0.2") == pytest.approx(0.3)
        assert calculate("10.0 / 4.0") == 2.5

    def test_error_cases(self):
        """Тест случаев с ошибками."""
        with pytest.raises(InvalidExpressionError):
            calculate("")
        with pytest.raises(InvalidExpressionError):
            calculate("2 + ")
        with pytest.raises(InvalidExpressionError):
            calculate("(2 + 3")
        with pytest.raises(InvalidExpressionError):
            calculate("2 + * 3")
        with pytest.raises(DivisionByZeroError):
            calculate("5 / 0")
        with pytest.raises(InvalidExpressionError):
            calculate("2 @ 3")

    def test_edge_cases(self):
        """Тест граничных случаев."""
        assert calculate("0") == 0
        assert calculate("1") == 1
        assert calculate("-0") == 0
        assert calculate("2 ** 0") == 1
        assert calculate("0 * 5") == 0


class TestIntegration:
    """Интеграционные тесты полного цикла вычислений."""

    def test_complex_real_world_expressions(self):
        """Тест сложных реальных выражений."""
        assert calculate("2 + 3 * (4 - 1)") == 11
        assert calculate("(2 + 3) * (4 - 1)") == 15
        assert calculate("-2 ** 3") == -8
        assert calculate("(-2) ** 3") == -8
        assert calculate("10 + 20 * 30") == 610
        assert calculate("2 * 3 + 4 * 5") == 26

    def test_expression_chain(self):
        """Тест цепочки выражений."""
        expressions = [
            ("1 + 1", 2),
            ("2 * 3", 6),
            ("10 - 4", 6),
            ("15 / 3", 5.0),
            ("2 ** 4", 16),
        ]
        
        for expr, expected in expressions:
            assert calculate(expr) == expected


def test_error_messages():
    """Тест сообщений об ошибках."""
    with pytest.raises(DivisionByZeroError):
        calculate("5 / 0")
    
    with pytest.raises(InvalidExpressionError):
        calculate("(2 + 3")