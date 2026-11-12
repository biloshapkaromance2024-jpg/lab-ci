import pytest

from shop.cart import Cart


@pytest.fixture
def my_cart() -> Cart:
    cart = Cart()
    cart.add("laptop", price=1500.0, qty=1)
    cart.add("mouse", price=50.0, qty=2)
    return cart
