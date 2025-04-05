"""Views for Grocery Instamart project."""

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .forms import RegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import Product, ProductCategory, Cart, CartItems, Profile

#welcom page view
def welcome(request):
    if request.user.is_authenticated:
        return redirect('products')
    return render(request, 'welcome.html')


def products(request):
    category_slug = request.GET.get('category')
    products_list = Product.objects.all()
    categories = ProductCategory.objects.all()

    if category_slug:
        products_list = products_list.filter(
            category__category_name__iexact=category_slug.replace("-", " ")
        )

    return render(request, 'products.html', {
        'products': products_list,
        'selected_category': category_slug,
        'categories': categories
    })


def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('products')
        messages.error(request, "Invalid username or password.")
        return redirect('login')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('welcome')


def register_page(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            phone = form.cleaned_data['phone']
            Profile.objects.create(user=user, phone=phone, email=user.email)
            messages.success(request, f'Account created successfully for {user.username}!')
            return redirect('login')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


@login_required
def profile_update(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            profile = profile_form.save(commit=False)
            profile.email = user.email  # sync email
            profile.phone = profile_form.cleaned_data['phone']  # update phone
            profile.save()

            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile_update')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=profile)

    return render(request, 'profile_update.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required
def add_cart(request, product_uid):
    product = get_object_or_404(Product, uid=product_uid)
    cart, _ = Cart.objects.get_or_create(user=request.user, is_paid=False)
    cart_item, created = CartItems.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    return redirect('cart')


@login_required
def increase_qty(request, cart_item_uid):
    item = get_object_or_404(CartItems, uid=cart_item_uid, cart__user=request.user)
    item.quantity += 1
    item.save()
    return redirect('cart')


@login_required
def decrease_qty(request, cart_item_uid):
    item = get_object_or_404(CartItems, uid=cart_item_uid, cart__user=request.user)
    item.quantity -= 1
    if item.quantity <= 0:
        item.delete()
    else:
        item.save()
    return redirect('cart')


@login_required
def remove_cart_items(request, cart_item_uid):
    cart_item = get_object_or_404(
        CartItems,
        uid=cart_item_uid,
        cart__user=request.user,
        cart__is_paid=False
    )
    cart_item.delete()
    messages.success(request, "Item removed from cart successfully.")
    return redirect('cart')


@login_required
def cart(request):
    cart_obj, _ = Cart.objects.get_or_create(user=request.user, is_paid=False)
    cart_items = CartItems.objects.filter(cart=cart_obj)
    items_with_subtotals = [
        {'item': item, 'subtotal': item.product.price * item.quantity}
        for item in cart_items
    ]
    total_price = sum(item['subtotal'] for item in items_with_subtotals)
    context = {
        'cart_items': items_with_subtotals,
        'total_price': total_price,
        'user_profile': request.user.profile,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
    }
    return render(request, 'cart.html', context)


@login_required
def make_order(request):
    if request.method == 'POST':
        delivery_address = request.POST.get('delivery_address')
        cart_obj = get_object_or_404(Cart, user=request.user, is_paid=False)
        cart_obj.is_paid = True
        cart_obj.delivery_address = delivery_address
        cart_obj.save()

        cart_items = CartItems.objects.filter(cart=cart_obj)
        items_with_subtotals = [
            {'item': item, 'subtotal': item.product.price * item.quantity}
            for item in cart_items
        ]
        total_price = sum(item['subtotal'] for item in items_with_subtotals)

        subject = 'Order Confirmation - Grocery Instamart'
        html_message = render_to_string('email/order_email.html', {
            'user': request.user,
            'cart_items': items_with_subtotals,
            'total_price': total_price,
            'delivery_address': delivery_address
        })
        plain_message = strip_tags(html_message)

        send_mail(subject, plain_message, None, [request.user.email], html_message=html_message)

        context = {
            'user': request.user,
            'cart_items': items_with_subtotals,
            'total_price': total_price,
            'delivery_address': delivery_address
        }
        messages.success(request, "Order placed successfully!")
        return render(request, 'order_confirmation.html', context)

    return redirect('cart')


@login_required
def orders(request):
    past_orders = Cart.objects.filter(user=request.user, is_paid=True).order_by('-date')
    return render(request, 'orders.html', {'orders': past_orders})


@login_required
def checkout(request):
    cart_obj, _ = Cart.objects.get_or_create(user=request.user, is_paid=False)
    cart_items = CartItems.objects.filter(cart=cart_obj)
    items_with_subtotals = [
        {'item': item, 'subtotal': item.product.price * item.quantity}
        for item in cart_items
    ]
    total_price = sum(item['subtotal'] for item in items_with_subtotals)
    context = {
        'cart_items': items_with_subtotals,
        'total_price': total_price,
        'user_profile': request.user.profile
    }
    return render(request, 'order.html', context)
