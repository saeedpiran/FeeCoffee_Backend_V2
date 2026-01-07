from django.test import TestCase
from accounts_module.models import User
from .models import ShopProfile, Shop

# Create your tests here.


class ShopTestCase(TestCase):
    def test_shop_creation(self):
        user = User.objects.create(username='testuser', user_type='seller')
        profile = ShopProfile.objects.get(owner=user)
        shop = Shop.objects.get(profile=profile)
        self.assertEqual(shop.profile, profile)
