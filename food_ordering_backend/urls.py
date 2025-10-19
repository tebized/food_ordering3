from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Import the ProfileView from your api app
from api.views import ProfileView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ADDED: Direct path to the profile view to avoid router conflicts
    path('api/profile/', ProfileView.as_view(), name='profile'),

    # This includes all the router-generated URLs (users, orders, etc.)
    path('api/', include('api.urls')),
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # This adds the login/logout button to the browsable API
    path('api-auth/', include('rest_framework.urls')),
]

# This helper is for serving user-uploaded files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
