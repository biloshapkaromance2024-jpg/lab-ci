from unittest.mock import Mock

import pytest

from shop.cart import Cart


def test_empty_cart_initial_state() -> None:
    cart = Cart()
    assert cart.items_count() == 0
    assert cart.total() == 0.0


def test_items_count_after_adding(my_cart: Cart) -> None:
    # 1 ноутбук + 2 мишки = 3 товари
    assert my_cart.items_count() == 3


def test_add_existing_item_updates_quantity(my_cart: Cart) -> None:
    # У кошику вже є 2 мишки, додаємо ще 3, має стати 5 мишок (разом з ноутбуком = 6 товарів)
    my_cart.add("mouse", price=50.0, qty=3)
    assert my_cart.items_count() == 6


@pytest.mark.parametrize(("price", "qty"), [(-5.0, 1), (500.0, 0), (1200.0, -2)])
def test_add_invalid_values_raises_error(price: float, qty: int) -> None:
    cart = Cart()
    with pytest.raises(ValueError):
        cart.add("keyboard", price=price, qty=qty)


def test_remove_item_success(my_cart: Cart) -> None:
    my_cart.remove("laptop")
    assert my_cart.items_count() == 2  # Залишились лише 2 мишки
    with pytest.raises(KeyError):
        my_cart.remove("laptop")  # Повторне видалення має викликати помилку


def test_remove_nonexistent_item_raises_keyerror(my_cart: Cart) -> None:
    with pytest.raises(KeyError):
        my_cart.remove("monitor")


# Перевірка знижок на новій сумі (1600 грн)
@pytest.mark.parametrize(
    ("discount", "expected"), [(0, 1600.0), (10, 1440.0), (25, 1200.0), (100, 0.0)]
)
def test_total_with_various_discounts(my_cart: Cart, discount: float, expected: float) -> None:
    assert my_cart.total(discount_percent=discount) == pytest.approx(expected)


@pytest.mark.parametrize("invalid_discount", [-10.0, 150.0])
def test_total_invalid_discount_raises_valueerror(my_cart: Cart, invalid_discount: float) -> None:
    with pytest.raises(ValueError, match="discount_percent"):
        my_cart.total(discount_percent=invalid_discount)


def test_total_in_foreign_currency(my_cart: Cart) -> None:
    rates = Mock()
    rates.get_rate.return_value = 40.0  # Підміна: 1 EUR = 40 UAH

    # 1600 UAH / 40 = 40.0 EUR
    assert my_cart.total_in("EUR", rates) == 40.0
    rates.get_rate.assert_called_once_with("EUR")


def test_total_in_invalid_rate_raises(my_cart: Cart) -> None:
    rates = Mock()
    rates.get_rate.return_value = -5.0  # Негативний курс
    with pytest.raises(ValueError, match="rate"):
        my_cart.total_in("USD", rates)


# --- Тести для методу most_expensive (TDD) ---
def test_most_expensive_item_found(my_cart: Cart) -> None:
    item = my_cart.most_expensive()
    assert item is not None
    assert item.name == "laptop"
    assert item.price == 1500.0


def test_most_expensive_in_empty_cart() -> None:
    cart = Cart()
    assert cart.most_expensive() is None
