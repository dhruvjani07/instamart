from django.apps import AppConfig

class HomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # Default pk
    name = 'home'  

    def ready(self):
        """ This function executes when the Django app is loaded. """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        from .models import CartItems

        def get_cart_count(self):
            return CartItems.objects.filter(cart__is_paid=False, cart__user=self).count()

        User.add_to_class("get_cart_count", get_cart_count)  # Attach method to User model
