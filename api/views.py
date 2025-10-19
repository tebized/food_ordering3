from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend 

from .models import (
    User, Restaurant, MenuItem, Order, Addon, PaymentAccount, 
    Conversation, ChatMessage, ActivityLog, Rating
)
from .serializers import (
    UserSerializer, UserProfileSerializer, RestaurantSerializer, MenuItemSerializer, 
    OrderListSerializer, OrderDetailSerializer, AddonSerializer, PaymentAccountSerializer, 
    ConversationSerializer, ChatMessageSerializer, ActivityLogSerializer, RatingSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

# --- Profile View ---
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

# --- Chat ViewSets ---
class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all().order_by('-created_at')
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'customer':
            return self.queryset.filter(customer=user)
        elif user.role in ['sub_admin', 'restaurant_admin'] or user.is_superuser:
            return self.queryset
        return Conversation.objects.none()

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all().order_by('timestamp')
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        conversation_id = self.request.query_params.get('conversation')
        if conversation_id:
            return self.queryset.filter(conversation_id=conversation_id)
        return ChatMessage.objects.none()

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

# --- Restaurant and Menu ViewSets ---
class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [AllowAny]  # Allow public access for browsing

    def get_permissions(self):
        # Require authentication for write operations
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]  # Allow public read access
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        # For authenticated users, apply role-based filtering
        if self.request.user.is_authenticated:
            user = self.request.user
            if user.role == 'sub_admin' or user.is_superuser:
                return super().get_queryset()
            elif user.role == 'customer':
                return super().get_queryset()  # Customers can see all restaurants
            elif user.restaurant:
                return super().get_queryset().filter(id=user.restaurant.id)
            return Restaurant.objects.none()
        else:
            # For guests, return all restaurants
            return super().get_queryset()


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [AllowAny]  # Allow public access for browsing
    
    def get_permissions(self):
        # Require authentication for write operations
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]  # Allow public read access
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by restaurant if an ID is provided in the query params
        restaurant_id = self.request.query_params.get('restaurant')
        if restaurant_id:
            return queryset.filter(restaurant_id=restaurant_id)

        # For authenticated users, apply role-based filtering
        if self.request.user.is_authenticated:
            user = self.request.user
            if user.role == 'sub_admin' or user.is_superuser:
                return queryset # Superusers and sub-admins can see all items
            elif user.role == 'customer':
                return queryset # Customers can see all menu items
            elif user.restaurant:
                return queryset.filter(restaurant=user.restaurant) # Restaurant admins see only their restaurant's items
            return MenuItem.objects.none()
        else:
            # For guests, return all menu items
            return queryset

class AddonViewSet(viewsets.ModelViewSet):
    queryset = Addon.objects.all()
    serializer_class = AddonSerializer
    permission_classes = [AllowAny]  # Allow public access for browsing
    
    def get_permissions(self):
        # Require authentication for write operations
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]  # Allow public read access
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = super().get_queryset()

        restaurant_id = self.request.query_params.get('restaurant')
        if restaurant_id:
            return queryset.filter(restaurant_id=restaurant_id)

        # For authenticated users, apply role-based filtering
        if self.request.user.is_authenticated:
            user = self.request.user
            if user.role == 'sub_admin' or user.is_superuser:
                return queryset
            elif user.role == 'customer':
                return queryset # Customers can see all addons
            elif user.restaurant:
                return queryset.filter(restaurant=user.restaurant)
            return Addon.objects.none()
        else:
            # For guests, return all addons
            return queryset

class PaymentAccountViewSet(viewsets.ModelViewSet):
    queryset = PaymentAccount.objects.all()
    serializer_class = PaymentAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        restaurant_id = self.request.query_params.get('restaurant')
        if restaurant_id:
            return queryset.filter(restaurant_id=restaurant_id)

        if user.role == 'sub_admin' or user.is_superuser:
            return queryset
        elif user.restaurant:
            return queryset.filter(restaurant=user.restaurant)
            
        return PaymentAccount.objects.none()

# --- Order ViewSet ---
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at') 
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        if self.action == 'retrieve':
            return OrderDetailSerializer
        return OrderListSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        # Optimize queries by prefetching related objects
        queryset = queryset.select_related('customer', 'restaurant').prefetch_related(
            'orderitem_set__menu_item', 
            'orderitem_set__addon'
        )
        
        if user.role == 'customer':
            queryset = queryset.filter(customer=user)
        elif user.role == 'sub_admin' or user.is_superuser:
            # Sub-admins can see all orders
            pass 
        elif user.role == 'restaurant_admin' and user.restaurant:
            # Restaurant admins can only see orders that have been approved by sub-admin
            # They cannot see orders with status 'Pending Payment' or 'Pending Approval'
            queryset = queryset.filter(
                restaurant=user.restaurant
            ).exclude(
                status__in=['Pending Payment', 'Pending Approval']
            )
        
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    @action(detail=True, methods=['patch'])
    def mark_as_delivered(self, request, pk=None):
        """Mark order as delivered by customer"""
        order = self.get_object()
        
        # Only customers can mark their own orders as delivered
        if request.user.role != 'customer' or order.customer != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        # Only orders in 'Preparing' or 'Ready for Pickup' status can be marked as delivered
        if order.status not in ['Preparing', 'Ready for Pickup']:
            return Response({'error': 'Order must be in Preparing or Ready for Pickup status'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'Delivered'
        order.save()
        
        return Response({'status': 'Order marked as delivered'})

    @action(detail=True, methods=['patch'])
    def mark_as_ready_for_pickup(self, request, pk=None):
        """Mark order as ready for pickup by sub-admin"""
        order = self.get_object()
        
        # Only sub-admins can mark orders as ready for pickup
        if request.user.role != 'sub_admin' and not request.user.is_superuser:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        # Only orders in 'Preparing' status can be marked as ready for pickup
        if order.status != 'Preparing':
            return Response({'error': 'Order must be in Preparing status'}, status=status.HTTP_400_BAD_REQUEST)
        
        from django.utils import timezone
        
        order.status = 'Ready for Pickup'
        order.ready_for_pickup_at = timezone.now()
        order.save()
        
        return Response({'status': 'Order marked as ready for pickup'})

    @action(detail=True, methods=['patch'])
    def mark_as_ready_for_pickup_restaurant(self, request, pk=None):
        """Mark order as ready for pickup by restaurant admin"""
        order = self.get_object()
        
        # Only restaurant admins can use this endpoint
        if request.user.role != 'restaurant_admin' or not request.user.restaurant:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        # Restaurant admin can only mark orders from their own restaurant
        if order.restaurant != request.user.restaurant:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        # Only orders in 'Preparing' status can be marked as ready for pickup
        if order.status != 'Preparing':
            return Response({'error': 'Order must be in Preparing status'}, status=status.HTTP_400_BAD_REQUEST)
        
        from django.utils import timezone
        
        order.status = 'Ready for Pickup'
        order.ready_for_pickup_at = timezone.now()
        order.save()
        
        return Response({'status': 'Order marked as ready for pickup'})

    @action(detail=True, methods=['patch'])
    def mark_as_completed(self, request, pk=None):
        """Mark order as completed by sub-admin"""
        order = self.get_object()
        
        # Only sub-admins can mark orders as completed
        if request.user.role != 'sub_admin' and not request.user.is_superuser:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        # Only orders in 'Delivered' status can be marked as completed
        if order.status != 'Delivered':
            return Response({'error': 'Order must be in Delivered status'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'Completed'
        order.save()
        
        # Create activity log
        ActivityLog.objects.create(
            actor=request.user,
            restaurant=order.restaurant,
            order=order,
            action_type=ActivityLog.ActionType.ORDER_DELIVERED,
            details=f"Order {order.order_code} completed by {request.user.username}"
        )
        
        return Response({'status': 'Order marked as completed'})

    @action(detail=False, methods=['post'])
    def auto_deliver_orders(self, request):
        """Manually trigger auto-delivery check for orders ready for pickup"""
        # Only sub-admins can trigger auto-delivery
        if request.user.role != 'sub_admin' and not request.user.is_superuser:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        # Find orders that should be auto-delivered
        orders_to_auto_deliver = Order.objects.filter(
            status='Ready for Pickup',
            ready_for_pickup_at__isnull=False
        )
        
        auto_delivered_count = 0
        auto_delivered_orders = []
        
        for order in orders_to_auto_deliver:
            if order.should_auto_deliver():
                order.status = 'Delivered'
                order.save()
                auto_delivered_count += 1
                auto_delivered_orders.append({
                    'order_code': order.order_code,
                    'customer': order.customer.username,
                    'restaurant': order.restaurant.name
                })
        
        return Response({
            'message': f'Auto-delivered {auto_delivered_count} order(s)',
            'auto_delivered_orders': auto_delivered_orders
        })

# --- Rating ViewSet ---
class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'customer':
            return self.queryset.filter(customer=user)
        elif user.role in ['sub_admin', 'restaurant_admin'] or user.is_superuser:
            return self.queryset
        return Rating.objects.none()

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

# --- Activity Log ViewSet ---
class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'restaurant_admin' and user.restaurant:
            return ActivityLog.objects.filter(restaurant=user.restaurant)
        
        # Superusers and sub-admins can see all logs
        if user.role == 'sub_admin' or user.is_superuser:
            return ActivityLog.objects.all()
            
        return ActivityLog.objects.none()

