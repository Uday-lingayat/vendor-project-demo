from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def api_root(request):
    return JsonResponse({
        'message': 'Vendor-Supplier Dashboard API',
        'version': '2.0',
        'supported_user_types': ['vendor', 'supplier'],
        'endpoints': {
            'health_check': '/api/health/',
            'user_signup': '/api/signup/',
            'user_login': '/api/login/',
            'user_profile': '/api/whoami/',
            'user_logout': '/api/logout/',
            'admin_panel': '/admin/'
        },
        'documentation': {
            'postman_collection': 'Import the updated JSON collection for testing both vendor and supplier flows',
            'admin_interface': 'Available at /admin/ after creating superuser - manage both vendors and suppliers',
            'user_types': {
                'vendor': 'Companies looking to purchase materials and services',
                'supplier': 'Organizations providing materials and services'
            }
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api_root, name='api_root'),
    path('', include('accounts.urls')),
    path('accounts/', include('accounts.urls')),
]