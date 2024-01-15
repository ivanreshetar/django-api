'''Django admin customization.'''
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as t

from core import models


class UserAdmin(BaseUserAdmin):
    '''Define the admin pages for User model.'''
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (t('Personal Information'), {'fields': ('name',)}),
        (t('Permissions'), {'fields': (
            'is_active',
            'is_staff',
            'is_superuser',
        )}),
        (t('Important Dates'), {'fields': ('last_login',)}),
    )
    readonly_fields = ('last_login',)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser',
            ),
        }),
    )


admin.site.register(models.User, UserAdmin)
