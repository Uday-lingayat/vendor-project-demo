from django.contrib.auth.models import User
from django.db import models


class VendorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor_profile')
    company_name = models.CharField(max_length=255, blank=True, null=True)
    business_type = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    gst_number = models.CharField(max_length=30, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Vendor: {self.user.email} - {self.company_name or 'No Company Name'}"

    class Meta:
        verbose_name = "Vendor Profile"
        verbose_name_plural = "Vendor Profiles"



class SupplierProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='supplier_profile')
    organization_name = models.CharField(max_length=255, blank=True, null=True)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    gst_number = models.CharField(max_length=30, blank=True, null=True)
    pan_number = models.CharField(max_length=10, blank=True, null=True)
    business_category = models.CharField(max_length=100, blank=True, null=True)
    supply_capacity = models.CharField(max_length=200, blank=True, null=True)
    certifications = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Supplier: {self.user.email} - {self.organization_name or 'No Organization Name'}"

class SupplierInventory(models.Model):
    supplier = models.ForeignKey(SupplierProfile, on_delete=models.CASCADE, related_name='inventory')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='supplier_inventories')
    stock_quantity = models.PositiveIntegerField(default=0)
    custom_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # supplier-specific price
    added_on = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args: any, **kwargs: any):
        super().__init__(args, kwargs)
        self.id = None

    def __str__(self):
        return f"{self.product.name} - {self.supplier.organization_name}"

class SharedOrder(models.Model):
    supplier = models.ForeignKey(SupplierProfile, on_delete=models.CASCADE, related_name='supplier_orders')
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='vendor_shared_orders')
    order_id = models.CharField(max_length=50)
    item_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    progress = models.IntegerField(default=1)

    def __str__(self):
        return f"SharedOrder {self.order_id} - {self.item_name}"

# Helper function to determine user type
def get_user_type(user):
    """Determine if user is vendor or supplier"""
    if hasattr(user, 'vendor_profile'):
        return 'vendor'
    elif hasattr(user, 'supplier_profile'):
        return 'supplier'
    return None


def get_user_profile(user):
    """Get the appropriate profile for the user"""
    if hasattr(user, 'vendor_profile'):
        return user.vendor_profile
    elif hasattr(user, 'supplier_profile'):
        return user.supplier_profile
    return None

#class for json file to update the models.
class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.FloatField()
    rating = models.FloatField()
    rating_count = models.IntegerField()
    category = models.CharField(max_length=100)
    image = models.URLField()
    badge = models.CharField(max_length=50, blank=True)
    supplier = models.CharField(max_length=255)
    supplier_image = models.URLField()
    description = models.TextField()

    def __str__(self):
        return self.name

# accounts/models.py
class Order(models.Model):
    order_id = models.CharField(max_length=20)
    customer = models.CharField(max_length=255)
    item_name = models.CharField(max_length=255)
    progress = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='orders')

    def __str__(self):
        return f"{self.order_id} - {self.item_name}"


class SupplierAnalytics(models.Model):
    supplier = models.OneToOneField(SupplierProfile, on_delete=models.CASCADE, related_name='analytics')
    new_orders = models.PositiveIntegerField(default=0)
    active_products = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    revenue_labels = models.JSONField(default=list)
    revenue_data = models.JSONField(default=list)
    category_labels = models.JSONField(default=list)
    category_data = models.JSONField(default=list)

    def __str__(self):
        return f"Analytics for {self.supplier.organization_name}"
