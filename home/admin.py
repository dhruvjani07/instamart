from django.contrib import admin
from .models import ProductCategory, Product, Cart, CartItems, Profile


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name',)
    search_fields = ('category_name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price')  
    list_filter = ('category',)
    search_fields = ('name',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_paid', 'date', 'delivery_address')
    list_filter = ('is_paid', 'date')
    search_fields = ('user__username', 'delivery_address')


@admin.register(CartItems)
class CartItemsAdmin(admin.ModelAdmin):
    list_display = ('get_user', 'product', 'quantity', 'cart')
    list_filter = ('product',)
    search_fields = ('cart__user__username', 'product__title')

    def get_user(self, obj):
        return obj.cart.user.username
    get_user.short_description = 'User'
    get_user.admin_order_field = 'cart__user'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'email')
    search_fields = ('user__username', 'phone', 'email')
