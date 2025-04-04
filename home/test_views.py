
import pytest
from django.urls import reverse
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_welcome_view(client):
    response = client.get(reverse('welcome'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_user_registration(client):
    response = client.post(reverse('register'), {
        'username': 'testuser',
        'email': 'test@example.com',
        'phone': '+1234567890',
        'password1': 'StrongPass123',
        'password2': 'StrongPass123',
    })
    assert response.status_code == 302  # redirect to login after success
    assert User.objects.filter(username='testuser').exists()
