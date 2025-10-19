from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from .models import User, Restaurant, MenuItem, Order

class CustomUserCreationForm(UserCreationForm):
    # Explicitly define the custom fields for the creation form
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)
    restaurant = forms.ModelChoiceField(
        queryset=Restaurant.objects.all(),
        required=False,
        help_text="Required for users with the 'Restaurant Admin' role."
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data['role']
        user.restaurant = self.cleaned_data.get('restaurant')
        if commit:
            user.save()
        return user

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    # This defines the layout for the EDIT page of a user
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        ("Custom Fields", {"fields": ("role", "restaurant")}),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser",)},
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    # --- THE FIX IS HERE ---
    # We remove 'email' from this list because it's not part of the simple creation form.
    # This resolves the FieldError.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'role', 'restaurant', 'password', 'password2'),
        }),
    )

    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone_number')
    search_fields = ('name',)

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'price')
    list_filter = ('restaurant',)
    search_fields = ('name', 'restaurant__name')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_code', 'customer', 'restaurant', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'restaurant')
    search_fields = ('order_code', 'customer__username', 'restaurant__name')
    readonly_fields = ('created_at',)

