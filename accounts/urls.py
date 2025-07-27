from django.urls import path
from .views import (
    login_view,
    logout_view,
    signup_page,
    vendor_dashboard,
    supplier_dashboard,
    import_products_view,
    product_list,
    order_list,
    profile_view,
    create_order,
    supplier_dashboard_api,
    supplier_inventory_api,
    supplier_orders_api,
    supplier_inventory_update_api, supplier_inventory_add_api, supplier_inventory_delete_api,
)

urlpatterns = [
    # Auth & Dashboards
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('signup/', signup_page, name='signup_page'),
    path('vendor/dashboard/', vendor_dashboard, name='vendor-dashboard'),
    path('supplier/dashboard/', supplier_dashboard, name='supplier-dashboard'),

    # Products import
    path('import-products/', import_products_view, name='import-products'),

    # Vendor APIs (unchanged)
    path('api/products/', product_list, name='product-list'),
    path('api/orders/', order_list, name='order-list'),
    path('api/profile/', profile_view, name='profile-api'),
    path('api/create-order/', create_order, name='create-order'),

    # Supplier APIs (cleaned)
    path('supplier/api/dashboard/', supplier_dashboard_api, name='supplier-dashboard-api'),
    path('supplier/api/inventory/', supplier_inventory_api, name='supplier-inventory-api'),
    path('supplier/api/inventory/update/', supplier_inventory_update_api, name='supplier-inventory-update-api'),
    path('supplier/api/inventory/add/', supplier_inventory_add_api, name='supplier-inventory-add-api'),
    path('supplier/api/inventory/delete/<int:item_id>/', supplier_inventory_delete_api,
         name='supplier-inventory-delete-api'),
    path('supplier/api/orders/', supplier_orders_api, name='supplier-orders-api'),
]

# from django.urls import path
# from .views import (
#     # Auth
#     login_view, logout_view, signup_page,
#     # Dashboards
#     vendor_dashboard, supplier_dashboard,
#     # Products & Orders
#     import_products_view, product_list, order_list, profile_api, create_order, update_profile,
#     # Supplier APIs
#     supplier_dashboard_api, supplier_inventory_api, supplier_orders_api,
#     supplier_inventory_update_api, supplier_add_product_api
# )
#
# urlpatterns = [
#     # ---------- Auth ----------
#     path('login/', login_view, name='login'),
#     path('logout/', logout_view, name='logout'),
#     path('signup/', signup_page, name='signup_page'),
#
#     # ---------- Dashboards ----------
#     path('vendor/dashboard/', vendor_dashboard, name='vendor-dashboard'),
#     path('supplier/dashboard/', supplier_dashboard, name='supplier-dashboard'),
#
#     # ---------- Vendor APIs ----------
#     path('api/products/', product_list, name='product-list'),
#     path('api/orders/', order_list, name='order-list'),
#     path('api/profile/', profile_api, name='profile-api'),
#     path('api/create-order/', create_order, name='create-order'),
#     path('api/update-profile/', update_profile, name='update-profile'),
#
#     # ---------- Supplier APIs ----------
#     path('api/supplier/dashboard/', supplier_dashboard_api, name='supplier-dashboard-api'),
#     path('api/supplier/inventory/', supplier_inventory_api, name='supplier-inventory-api'),
#     path('api/supplier/inventory/update/', supplier_inventory_update_api, name='supplier-inventory-update-api'),
#     path('api/supplier/inventory/add/', supplier_add_product_api, name='supplier-inventory-add-api'),
#     path('api/supplier/orders/', supplier_orders_api, name='supplier-orders-api'),
#
#     # ---------- Data Import ----------
#     path('import-products/', import_products_view, name='import-products'),
# ]