from rest_framework import serializers
from django.contrib.auth.models import User
from .models import VendorProfile, SupplierProfile, Product, Order, SupplierInventory


# --------- Registration ----------
class UserRegistrationSerializer(serializers.Serializer):
    USER_TYPE_CHOICES = [
        ('vendor', 'Vendor'),
        ('supplier', 'Supplier'),
    ]
    user_type = serializers.ChoiceField(choices=USER_TYPE_CHOICES)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)
    first_name = serializers.CharField(max_length=30, required=False)
    last_name = serializers.CharField(max_length=30, required=False)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value


class VendorRegistrationSerializer(serializers.Serializer):
    company_name = serializers.CharField(max_length=255, required=False)
    business_type = serializers.CharField(max_length=100, required=False)
    phone = serializers.CharField(max_length=20, required=False)
    address = serializers.CharField(required=False)
    gst_number = serializers.CharField(max_length=30, required=False)
    website = serializers.URLField(required=False)


class SupplierRegistrationSerializer(serializers.Serializer):
    organization_name = serializers.CharField(max_length=255, required=False)
    contact_person = serializers.CharField(max_length=100, required=False)
    phone = serializers.CharField(max_length=20, required=False)
    address = serializers.CharField(required=False)
    gst_number = serializers.CharField(max_length=30, required=False)
    pan_number = serializers.CharField(max_length=10, required=False)
    business_category = serializers.CharField(max_length=100, required=False)
    supply_capacity = serializers.CharField(max_length=200, required=False)
    certifications = serializers.CharField(required=False)
    website = serializers.URLField(required=False)


# --------- Login ----------
class UserLoginSerializer(serializers.Serializer):
    USER_TYPE_CHOICES = [
        ('vendor', 'Vendor'),
        ('supplier', 'Supplier'),
    ]
    user_type = serializers.ChoiceField(choices=USER_TYPE_CHOICES)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


# --------- Vendor & Supplier Profiles ----------
class VendorProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = VendorProfile
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()


class SupplierProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = SupplierProfile
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()


# --------- User Profile (Unified) ----------
class UserProfileSerializer(serializers.ModelSerializer):
    user_type = serializers.SerializerMethodField()
    profile_data = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name',
                  'date_joined', 'user_type', 'profile_data']
        read_only_fields = ['id', 'username', 'date_joined']

    def get_user_type(self, obj):
        if hasattr(obj, 'vendor_profile'):
            return 'vendor'
        elif hasattr(obj, 'supplier_profile'):
            return 'supplier'
        return None

    def get_profile_data(self, obj):
        if hasattr(obj, 'vendor_profile'):
            return VendorProfileSerializer(obj.vendor_profile).data
        elif hasattr(obj, 'supplier_profile'):
            return SupplierProfileSerializer(obj.supplier_profile).data
        return None


# --------- Products ----------
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


# --------- Orders ----------
class OrderSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.company_name', read_only=True)  # <-- add vendor name
    class Meta:
        model = Order
        fields = ['id', 'order_id', 'customer', 'item_name', 'date', 'amount', 'progress', 'vendor', 'vendor_name']

# class SupplierInventorySerializer(serializers.ModelSerializer):
#     product_id = serializers.IntegerField(source='product.id', read_only=True)
#     product_name = serializers.CharField(source='product.name', read_only=True)
#     category = serializers.CharField(source='product.category', read_only=True)
#     image = serializers.CharField(source='product.image', read_only=True)
#     description = serializers.CharField(source='product.description', read_only=True)
#     price = serializers.SerializerMethodField()
#
#     class Meta:
#         model = SupplierInventory
#         fields = ['id', 'product_id', 'product_name', 'category', 'image', 'description', 'price', 'stock_quantity']
#
#     def get_price(self, obj):
#         return obj.custom_price or obj.product.price