from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import VendorProfile, SupplierProfile


@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'company_name', 'business_type', 'phone', 'is_verified', 'created_at']
    list_filter = ['business_type', 'is_verified', 'created_at', 'updated_at']
    search_fields = ['user__email', 'company_name', 'phone', 'gst_number']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_verified']

    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Company Details', {
            'fields': ('company_name', 'business_type', 'phone', 'address', 'website')
        }),
        ('Business Information', {
            'fields': ('gst_number', 'is_verified')
        }),
    )


@admin.register(SupplierProfile)
class SupplierProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'organization_name', 'contact_person', 'business_category', 'is_verified', 'created_at']
    list_filter = ['business_category', 'is_verified', 'created_at', 'updated_at']
    search_fields = ['user__email', 'organization_name', 'contact_person', 'phone', 'gst_number', 'pan_number']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_verified']

    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Organization Details', {
            'fields': ('organization_name', 'contact_person', 'phone', 'address', 'website')
        }),
        ('Business Information', {
            'fields': ('business_category', 'supply_capacity', 'certifications')
        }),
        ('Legal Information', {
            'fields': ('gst_number', 'pan_number', 'is_verified')
        }),

    )


# Extend the default User admin to show profiles
class VendorProfileInline(admin.StackedInline):
    model = VendorProfile
    can_delete = False
    verbose_name_plural = 'Vendor Profile'
    fk_name = 'user'


class SupplierProfileInline(admin.StackedInline):
    model = SupplierProfile
    can_delete = False
    verbose_name_plural = 'Supplier Profile'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (VendorProfileInline, SupplierProfileInline)

    def get_inline_instances(self, request, obj=None):
        """Only show relevant inline based on user's profile"""
        if obj:
            if hasattr(obj, 'vendor_profile'):
                return [VendorProfileInline(self.model, self.admin_site)]
            elif hasattr(obj, 'supplier_profile'):
                return [SupplierProfileInline(self.model, self.admin_site)]
        return []


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Custom admin site configuration
admin.site.site_header = "Vendor-Supplier Dashboard Admin"
admin.site.site_title = "Vendor-Supplier Admin Portal"
admin.site.index_title = "Welcome to Vendor-Supplier Dashboard Administration"