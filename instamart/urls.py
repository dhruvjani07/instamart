from django.urls import path
from django.contrib import admin
from home.views import (
    welcome, login_page, register_page, logout_view,
    profile_update, products,
    add_cart, cart, remove_cart_items, increase_qty, decrease_qty,
    make_order, orders
)
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', welcome, name='welcome'),
    path('login/', login_page, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_page, name='register'),
    path('profile_update/', login_required(profile_update), name='profile_update'),

    path('products/', login_required(products), name='products'),

    path('add_cart/<uuid:product_uid>/', login_required(add_cart), name='add_cart'),
    path('increase/<uuid:cart_item_uid>/', login_required(increase_qty), name='increase_qty'),
    path('decrease/<uuid:cart_item_uid>/', login_required(decrease_qty), name='decrease_qty'),
    path('remove_cart_items/<uuid:cart_item_uid>/', login_required(remove_cart_items), name='remove_cart_items'),

    path('cart/', login_required(cart), name='cart'),
    path('make_order/', login_required(make_order), name='make_order'),
    path('orders/', login_required(orders), name='orders'),

    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
