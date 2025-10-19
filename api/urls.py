from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'restaurants', views.RestaurantViewSet)
router.register(r'menu-items', views.MenuItemViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'addons', views.AddonViewSet)
router.register(r'payment-accounts', views.PaymentAccountViewSet)
router.register(r'conversations', views.ConversationViewSet)
router.register(r'chat-messages', views.ChatMessageViewSet)
router.register(r'ratings', views.RatingViewSet)

# The 'profile' path has been removed from here and moved to the main urls.py
urlpatterns = [
    path('', include(router.urls)),
]

