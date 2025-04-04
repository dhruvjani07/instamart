from django.db import models
from django.contrib.auth.models import User 
import uuid

# BaseModel for common fields
class BaseModel(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        abstract = True

# Product category (e.g., fruits, snacks, cold drinks)
class ProductCategory(BaseModel):
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return self.category_name

# Grocery item
class Product(BaseModel):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=100)
    price = models.IntegerField(default=100)
    image = models.ImageField(upload_to='products')

    def __str__(self):
        return self.name

# User shopping cart
class Cart(BaseModel):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='carts')
    is_paid = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    delivery_address = models.TextField(null=True, blank=True)

    def get_cart_total(self):
        total = CartItems.objects.filter(cart=self).aggregate(
            total_price=models.Sum(models.F('product__price') * models.F('quantity'), output_field=models.IntegerField())
        )['total_price']
        return total if total is not None else 0

    def __str__(self):
        return f"Cart - {self.user.username} | Paid: {self.is_paid}" if self.user else "Cart - Guest"

    class Meta:
        ordering = ['-date']

# Items within a cart
class CartItems(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.product.name} in Cart"

# Extended user profile info
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)

    def __str__(self):
        return self.user.username
    
