import json, os
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import (
    VendorProfile, SupplierProfile, Product, Order,
    SupplierInventory, SharedOrder, get_user_type
)
from .serializers import (
    ProductSerializer, OrderSerializer, UserProfileSerializer, VendorProfileSerializer
)
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.middleware.csrf import get_token

@ensure_csrf_cookie
def get_csrf_token(request):
    """
    Returns the CSRF token for use in frontend fetch() calls.
    """
    return JsonResponse({'csrfToken': get_token(request)})
# -------------------- AUTH & SIGNUP --------------------
def signup_page(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        user_type = request.POST.get("user_type")

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered!")
            return render(request, 'signup.html')

        # Create user
        user = User.objects.create_user(username=email, email=email, password=password,
                                        first_name=first_name, last_name=last_name)

        if user_type == "vendor":
            VendorProfile.objects.create(
                user=user,
                company_name=request.POST.get("company_name"),
                business_type=request.POST.get("business_type"),
                phone=request.POST.get("vendor_phone"),
                address=request.POST.get("vendor_address"),
                gst_number=request.POST.get("vendor_gst_number"),
                website=request.POST.get("vendor_website"),
            )
        elif user_type == "supplier":
            SupplierProfile.objects.create(
                user=user,
                organization_name=request.POST.get("organization_name"),
                contact_person=request.POST.get("contact_person"),
                phone=request.POST.get("supplier_phone"),
                address=request.POST.get("supplier_address"),
                gst_number=request.POST.get("supplier_gst_number"),
                pan_number=request.POST.get("supplier_pan_number"),
                business_category=request.POST.get("supplier_business_category"),
                supply_capacity=request.POST.get("supplier_supply_capacity"),
                certifications=request.POST.get("supplier_certifications"),
                website=request.POST.get("supplier_website"),
            )

        messages.success(request, "Signup successful! Please log in.")
        return redirect('login')

    return render(request, 'signup.html')


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(username=email, password=password)
        if user:
            login(request, user)
            user_type = get_user_type(user)
            if user_type == 'vendor':
                return redirect('vendor-dashboard')
            elif user_type == 'supplier':
                return redirect('supplier-dashboard')
            else:
                messages.error(request, "Profile type missing.")
                return redirect('login')
        else:
            messages.error(request, "Invalid email or password")
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


# -------------------- DASHBOARD RENDERS --------------------
@login_required
def vendor_dashboard(request):
    vendor_profile = VendorProfile.objects.filter(user=request.user).first()
    if not vendor_profile:
        return render(request, 'error.html', {"message": "You are not a vendor!"})
    orders = Order.objects.filter(vendor=vendor_profile).order_by('-date')
    products = Product.objects.all()
    return render(request, 'dashboard.html', {
        'vendor': vendor_profile,
        'orders': orders,
        'products': products,
    })


@login_required
def supplier_dashboard(request):
    return render(request, 'dashboard2.html')


# -------------------- PRODUCTS --------------------
def import_products_view(request):
    file_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'products.json')
    if not os.path.exists(file_path):
        return HttpResponse("products.json not found.", status=404)

    with open(file_path, 'r') as file:
        products = json.load(file)
        for p in products:
            Product.objects.update_or_create(
                id=p['id'],
                defaults={
                    'name': p['name'],
                    'price': p['price'],
                    'rating': p['rating'],
                    'rating_count': p['ratingCount'],
                    'category': p['category'],
                    'image': p['image'],
                    'badge': p['badge'],
                    'supplier': p['supplier'],
                    'supplier_image': p['supplierImage'],
                    'description': p['description'],
                }
            )
    return HttpResponse("Products imported successfully!")


@api_view(['GET'])
@permission_classes([AllowAny])
def product_list(request):
    category = request.GET.get('category')
    products = Product.objects.all()
    if category:
        products = products.filter(category__iexact=category)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


# -------------------- VENDOR APIs --------------------
@login_required
def orders_api(request):
    orders = Order.objects.all().values()
    return JsonResponse(list(orders), safe=False)


@login_required
def profile_api(request):
    if hasattr(request.user, 'vendor_profile'):
        profile = VendorProfileSerializer(request.user.vendor_profile).data
        return JsonResponse(profile)
    return JsonResponse({"error": "Not authenticated"}, status=401)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def order_list(request):
    vendor_profile = request.user.vendor_profile
    if request.method == 'POST':
        items = request.data.get('items', [])
        created_orders = []
        for item in items:
            order = Order.objects.create(
                vendor=vendor_profile,
                order_id=f"ORD{Order.objects.count() + 1:03d}",
                customer=f"{request.user.first_name} {request.user.last_name}".strip(),
                item_name=item['name'],
                amount=item['price'] * item['quantity'],
                progress=1,
                date=timezone.now()
            )
            created_orders.append(order)
        return Response({"success": True, "message": "Orders created successfully."})

    orders = Order.objects.filter(vendor=vendor_profile).order_by('-date')
    current_orders = orders.filter(progress__lt=3)
    recent_orders = orders.filter(progress=3)[:5]
    return Response({
        "currentOrders": OrderSerializer(current_orders, many=True).data,
        "recentOrders": OrderSerializer(recent_orders, many=True).data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    data = request.data
    full_name = data.get('full_name', '')
    if full_name:
        parts = full_name.strip().split(" ", 1)
        user.first_name = parts[0]
        user.last_name = parts[1] if len(parts) > 1 else ''
        user.save()

    if hasattr(user, 'vendor_profile'):
        vendor_profile = user.vendor_profile
        vendor_profile.company_name = data.get('company_name', vendor_profile.company_name)
        vendor_profile.address = data.get('address', vendor_profile.address)
        vendor_profile.save()
    elif hasattr(user, 'supplier_profile'):
        supplier_profile = user.supplier_profile
        supplier_profile.organization_name = data.get('company_name', supplier_profile.organization_name)
        supplier_profile.address = data.get('address', supplier_profile.address)
        supplier_profile.save()

    return Response({"success": True, "message": "Profile updated successfully"})


# -------------------- SUPPLIER APIs --------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def supplier_dashboard_api(request):
    # Ensure the user has a supplier profile
    if not hasattr(request.user, 'supplier_profile'):
        return Response({"error": "No supplier profile found"}, status=status.HTTP_403_FORBIDDEN)

    supplier = request.user.supplier_profile

    # Stats
    new_orders = SharedOrder.objects.filter(supplier=supplier).count()
    active_products = SupplierInventory.objects.filter(supplier=supplier).count()
    total_revenue = SharedOrder.objects.filter(supplier=supplier).aggregate(Sum('amount'))['amount__sum'] or 0

    # Category breakdown (handle missing product safely)
    categories = SupplierInventory.objects.filter(supplier=supplier, product__isnull=False).values(
        'product__category'
    ).annotate(count=Count('id'))
    category_labels = [c['product__category'] for c in categories]
    category_data = [c['count'] for c in categories]

    # Revenue chart (we can later make it dynamic based on order dates)
    revenue_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    revenue_data = [15000, 19000, 22000, 18000, 24000, 28000]  # Placeholder

    return Response({
        "stats": {
            "newOrders": new_orders,
            "activeProducts": active_products,
            "revenue": total_revenue
        },
        "revenueChart": {"labels": revenue_labels, "data": revenue_data},
        "categoryChart": {"labels": category_labels, "data": category_data}
    })


@login_required
def supplier_inventory_api(request):
    supplier = request.user.supplier_profile
    inventory = SupplierInventory.objects.filter(supplier=supplier).select_related('product')
    data = [
        {
            "id": inv.id,
            "product_name": inv.product.name,
            "category": inv.product.category,
            "price": inv.custom_price or inv.product.price,
            "stock_quantity": inv.stock_quantity,
            "image": inv.product.image,
            "description": inv.product.description
        }
        for inv in inventory
    ]
    return Response(data)

@login_required
def supplier_orders_api(request):
    supplier = request.user.supplier_profile
    orders = SharedOrder.objects.filter(supplier=supplier).values()
    return Response(list(orders))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def supplier_inventory_update_api(request):
    supplier = request.user.supplier_profile
    item_id = request.data.get('id')
    stock = request.data.get('stock_quantity')
    price = request.data.get('custom_price')

    try:
        inventory_item = SupplierInventory.objects.get(id=item_id, supplier=supplier)
    except SupplierInventory.DoesNotExist:
        return Response({"error": "Item not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND)

    if stock is not None:
        inventory_item.stock_quantity = stock
    if price is not None:
        inventory_item.custom_price = price
    inventory_item.save()

    return Response({"success": True, "message": "Inventory updated successfully!"})
# Optional: For adding new products (uncomment if needed)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def supplier_add_product_api(request):
    supplier = request.user.supplier_profile
    product_id = request.data.get('product_id')
    stock = request.data.get('stock_quantity', 0)
    price = request.data.get('custom_price', None)
    try:
        product = Product.objects.get(id=product_id)
        SupplierInventory.objects.create(supplier=supplier, product=product, stock_quantity=stock, custom_price=price)
        return Response({"success": True, "message": "Product added to inventory!"})
    except Product.DoesNotExist:
        return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """
    Create orders for the logged-in vendor from cart items
    """
    vendor_profile = getattr(request.user, 'vendor_profile', None)
    if not vendor_profile:
        return Response({"error": "Only vendors can place orders"}, status=status.HTTP_403_FORBIDDEN)

    cart_items = request.data.get('cart', [])
    if not cart_items:
        return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

    created_orders = []
    for item in cart_items:
        order = Order.objects.create(
            vendor=vendor_profile,
            order_id=f"ORD{Order.objects.count() + 1:03d}",
            customer=vendor_profile.company_name or request.user.get_full_name(),
            item_name=item['name'],
            progress=1,
            amount=item['price'] * item['quantity'],
            date=timezone.now()
        )
        created_orders.append(order)

    return Response(OrderSerializer(created_orders, many=True).data, status=status.HTTP_201_CREATED)


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def profile_view(request):
#     """
#     Unified profile API for both vendors and suppliers.
#     Includes basic user data + profile fields.
#     """
#     user = request.user
#     base_data = {
#         "first_name": user.first_name,
#         "last_name": user.last_name,
#         "email": user.email,
#         # "vendor-type": user.vendor_type,
#     }
#
#     if hasattr(user, 'vendor_profile'):
#         profile = VendorProfileSerializer(user.vendor_profile).data
#         profile.update(base_data)
#     elif hasattr(user, 'supplier_profile'):
#         supplier_profile = user.supplier_profile
#         profile = {
#             **base_data,
#             "organization_name": supplier_profile.organization_name,
#             "contact_person": supplier_profile.contact_person,
#             "phone": supplier_profile.phone,
#             "address": supplier_profile.address,
#             "gst_number": supplier_profile.gst_number,
#             "business_category": supplier_profile.business_category,
#             "website": supplier_profile.website,
#         }
#     else:
#         return Response({"error": "Profile not found"}, status=404)
#
#     return Response(profile)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    Unified profile view for vendors and suppliers.
    Returns user info + vendor/supplier profile data.
    """
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def supplier_inventory_add_api(request):
    """
    Add a new product for the supplier and ensure it appears in vendor shop.
    """
    user = request.user
    if not hasattr(user, 'supplier_profile'):
        return Response({"error": "You are not a supplier"}, status=status.HTTP_403_FORBIDDEN)

    supplier = user.supplier_profile
    data = request.data

    # Validate required fields
    required_fields = ['name', 'category', 'price', 'stock_quantity']
    for field in required_fields:
        if not data.get(field):
            return Response({"error": f"{field} is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Step 1: Create Product
        product = Product.objects.create(
            name=data['name'],
            price=data['price'],
            rating=data.get('rating', 0),
            rating_count=data.get('rating_count', 0),
            category=data['category'],
            image=data.get('image', 'https://cdn-icons-png.flaticon.com/512/3081/3081559.png'),
            badge=data.get('badge', ''),
            supplier=supplier.organization_name,
            supplier_image=data.get('supplier_image', 'https://randomuser.me/api/portraits/men/1.jpg'),
            description=data.get('description', '')
        )

        # Step 2: Add to SupplierInventory
        SupplierInventory.objects.create(
            supplier=supplier,
            product=product,
            stock_quantity=data['stock_quantity'],
            custom_price=data.get('custom_price') or None
        )

        return Response({
            "id": product.id,
            "name": product.name,
            "category": product.category,
            "price": product.price,
            "stock_quantity": data['stock_quantity'],
            "image": product.image,
            "description": product.description
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": f"Failed to save product: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def supplier_inventory_delete_api(request, pk):
    """Delete product (both SupplierInventory & Product)."""
    supplier = request.user.supplier_profile
    try:
        inventory_item = SupplierInventory.objects.get(id=pk, supplier=supplier)
    except SupplierInventory.DoesNotExist:
        return Response({"error": "Product not found or unauthorized"}, status=404)

    product = inventory_item.product
    inventory_item.delete()
    product.delete()

    return Response({"success": True, "message": "Product deleted successfully"})
