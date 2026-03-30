import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .managers import CustomUserManager

class CustomUser(AbstractBaseUser, PermissionsMixin):
    login_id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False, unique=True)

    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)

    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)

    is_email_verified = models.BooleanField(default=False)
    telegram_chat_id = models.CharField(max_length=50, blank=True, null=True)
    timezone = models.CharField(max_length=50, default='Asia/Kolkata')

    # Changed to be agnostic. Can hold a Razorpay, Cashfree, or Stripe ID later!
    payment_gateway_id = models.CharField(max_length=255, blank=True, null=True)
    subscription_tier = models.CharField(max_length=50, default='free')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self) -> str:
        return (self.email or self.phone_number or str(self.login_id))

