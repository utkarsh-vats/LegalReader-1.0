from django.contrib import admin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('login_id', 'email', 'phone_number', 'first_name', 'last_name', 'created_at', 'updated_at')
    search_fields = ('login_id', 'email', 'phone_number', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_staff', 'is_email_verified', 'subscription_tier')