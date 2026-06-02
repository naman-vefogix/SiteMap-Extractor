from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, SitemapExtraction


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = (
        "id",
        "username",
        "email",
        "email_is_verify",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "is_staff",
        "is_active",
        "email_is_verify",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "Custom Fields",
            {
                "fields": (
                    "email_is_verify",
                )
            },
        ),
    )


@admin.register(SitemapExtraction)
class SitemapExtractionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "domain",
        "total_urls",
        "status",
        "created_at",
        "expires_at",
    )

    search_fields = (
        "domain",
        "user__email",
        "user__username",
    )

    list_filter = (
        "status",
        "created_at",
    )