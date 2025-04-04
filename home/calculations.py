from .models import CartItems

def calculate_total(cart_items):
    """
    Calculate the total price of items in a cart.
    """
    return sum(item.pizza.price * item.quantity for item in cart_items)  # Compute total price
