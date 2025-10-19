import json
from rest_framework import serializers
from .models import User, Restaurant, MenuItem, Order, Addon, PaymentAccount, OrderItem, Conversation, ChatMessage, ActivityLog, Rating

# --- User Serializers ---

class UserSerializer(serializers.ModelSerializer):
    restaurant = serializers.PrimaryKeyRelatedField(queryset=Restaurant.objects.all(), required=False, allow_null=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'restaurant', 'is_superuser']
        extra_kwargs = { 'password': {'write_only': True}, 'is_superuser': {'read_only': True} }
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']

# --- Restaurant and Menu Serializers ---

class PaymentAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentAccount
        fields = ['id', 'restaurant', 'account_type', 'account_number']

class RestaurantSerializer(serializers.ModelSerializer):
    payment_accounts = PaymentAccountSerializer(many=True, read_only=True)
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address', 'phone_number', 'logo', 'payment_accounts']

# NEW: A simple serializer to get just the restaurant's name
class SimpleRestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['name']

# UPDATED: Serializer for the profile endpoint, now includes username and restaurant name
class UserProfileSerializer(serializers.ModelSerializer):
    restaurant = SimpleRestaurantSerializer(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'restaurant']


class MenuItemSerializer(serializers.ModelSerializer):
    average_rating = serializers.ReadOnlyField()
    rating_count = serializers.ReadOnlyField()
    
    class Meta:
        model = MenuItem
        fields = '__all__'

class AddonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Addon
        fields = '__all__'

class RatingSerializer(serializers.ModelSerializer):
    customer_username = serializers.CharField(source='customer.username', read_only=True)
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    
    class Meta:
        model = Rating
        fields = ['id', 'menu_item', 'menu_item_name', 'customer', 'customer_username', 'stars', 'comment', 'created_at']
        read_only_fields = ['customer', 'customer_username', 'menu_item_name', 'created_at']

# --- Order Serializers ---

# For displaying simplified item details within an order
class SimpleMenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['name', 'price', 'image']

class SimpleAddonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Addon
        fields = ['name', 'price']

class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_details = SimpleMenuItemSerializer(source='menu_item', read_only=True)
    addon_details = SimpleAddonSerializer(source='addon', read_only=True)
    # Add these fields for backward compatibility
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    menu_item_price = serializers.DecimalField(source='menu_item.price', max_digits=8, decimal_places=2, read_only=True)
    addon_name = serializers.CharField(source='addon.name', read_only=True)
    addon_price = serializers.DecimalField(source='addon.price', max_digits=8, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'quantity', 'menu_item', 'addon', 'menu_item_details', 'addon_details', 'menu_item_name', 'menu_item_price', 'addon_name', 'addon_price']


# For the DETAILED view of a single order
class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source='orderitem_set', many=True, read_only=True)
    restaurant = RestaurantSerializer(read_only=True)
    customer = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'order_code', 'total_price', 'status', 'payment_proof', 'items', 'restaurant', 'customer', 'created_at']

# For the LIST view of all orders and for CREATING a new order
class OrderListSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(source='orderitem_set', many=True, read_only=True)
    customer_details = SimpleUserSerializer(source='customer', read_only=True)
    restaurant_details = SimpleRestaurantSerializer(source='restaurant', read_only=True)
    items = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'customer_details', 'restaurant', 'restaurant_details', 'order_items', 'items', 'total_price', 'status', 'payment_proof', 'order_code', 'created_at']
        read_only_fields = ['order_code', 'total_price', 'customer']

    def create(self, validated_data):
        validated_data['customer'] = self.context['request'].user
        items_json = validated_data.pop('items')
        items_data = json.loads(items_json)
        
        order = Order.objects.create(**validated_data)
        
        total_price = 0
        order_items_to_create = []

        for item_data in items_data:
            quantity = item_data['quantity']
            menu_item_id = item_data.get('menu_item_id')
            addon_id = item_data.get('addon_id')

            if menu_item_id:
                menu_item = MenuItem.objects.get(id=menu_item_id)
                order_items_to_create.append(OrderItem(order=order, menu_item=menu_item, quantity=quantity))
                total_price += menu_item.price * quantity
            elif addon_id:
                addon = Addon.objects.get(id=addon_id)
                order_items_to_create.append(OrderItem(order=order, addon=addon, quantity=quantity))
                total_price += addon.price * quantity

        if order_items_to_create:
            OrderItem.objects.bulk_create(order_items_to_create)

        order.total_price = total_price
        order.save()

        # *** THE FIX IS HERE ***
        # Refresh the order instance from the DB to include the newly created items
        order.refresh_from_db()
        
        return order


# --- Chat Serializers ---

class ChatMessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    class Meta:
        model = ChatMessage
        fields = ['id', 'conversation', 'sender', 'sender_username', 'message', 'timestamp']
        read_only_fields = ['sender', 'sender_username', 'timestamp']

class ConversationSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    customer_username = serializers.CharField(source='customer.username', read_only=True)
    class Meta:
        model = Conversation
        fields = ['id', 'customer', 'customer_username', 'subject', 'created_at', 'is_open', 'messages']
        read_only_fields = ['customer', 'customer_username', 'created_at']


# --- Activity Log Serializer (Corrected) ---
class ActivityLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.username', read_only=True)
    order_code = serializers.CharField(source='order.order_code', read_only=True)

    class Meta:
        model = ActivityLog
        fields = ['id', 'action_type', 'actor_name', 'order_code', 'timestamp']

