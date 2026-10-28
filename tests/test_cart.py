import pytest
from unittest.mock import Mock
from shop.cart import Cart
def test_cart_initialization(empty_cart: Cart) -> None:
    assert empty_cart.items_count() == 0
def test_add_new_item(empty_cart: Cart) -> None:
    empty_cart.add("book", 200.0, 1)
    assert empty_cart.items_count() == 1
def test_add_existing_item(empty_cart: Cart) -> None:
    empty_cart.add("book", 200.0, 2)
    empty_cart.add("book", 250.0, 3)
    assert empty_cart.items_count() == 5
def test_add_negative_price_raises(empty_cart: Cart) -> None:
    with pytest.raises(ValueError, match="price"):
        empty_cart.add("book", -10.0)
@pytest.mark.parametrize("qty", [0, -1, -100])
def test_add_invalid_qty_raises(empty_cart: Cart, qty: int) -> None:
    with pytest.raises(ValueError, match="qty"):
        empty_cart.add("book", 200.0, qty)
def test_remove_item(cart_with_items: Cart) -> None:
    cart_with_items.remove("book")
    assert cart_with_items.items_count() == 5
def test_remove_missing_item_raises(empty_cart: Cart) -> None:
    with pytest.raises(KeyError):
        empty_cart.remove("not_exist")
def test_total_no_discount(cart_with_items: Cart) -> None:
    assert cart_with_items.total() == pytest.approx(510.0)
@pytest.mark.parametrize(
    ("discount", "expected"),
    [
        (0, 510.0),
        (10, 459.0),
        (50, 255.0),
        (100, 0.0),
    ],
)
def test_total_with_discount(cart_with_items: Cart, discount: float, expected: float) -> None:
    assert cart_with_items.total(discount_percent=discount) == pytest.approx(expected)
@pytest.mark.parametrize("discount", [-1, 101, 150])
def test_total_invalid_discount_raises(cart_with_items: Cart, discount: float) -> None:
    with pytest.raises(ValueError, match="discount"):
        cart_with_items.total(discount_percent=discount)
def test_total_in_currency(cart_with_items: Cart) -> None:
    mock_rates = Mock()
    mock_rates.get_rate.return_value = 40.0
    expected_total = round(510.0 / 40.0, 2)
    assert cart_with_items.total_in("USD", mock_rates) == expected_total
    mock_rates.get_rate.assert_called_once_with("USD")
def test_total_in_invalid_rate_raises(cart_with_items: Cart) -> None:
    mock_rates = Mock()
    mock_rates.get_rate.return_value = -5.0
    with pytest.raises(ValueError, match="rate must be positive"):
        cart_with_items.total_in("USD", mock_rates)
def test_most_expensive_empty(empty_cart: Cart) -> None:
    assert empty_cart.most_expensive() is None
def test_most_expensive_with_items(cart_with_items: Cart) -> None:
    most_exp = cart_with_items.most_expensive()
    assert most_exp is not None
    assert most_exp.name == "book"
    assert most_exp.price == 200.0
