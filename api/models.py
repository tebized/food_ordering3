from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('restaurant_admin', 'Restaurant Admin'),
        ('sub_admin', 'Sub Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    restaurant = models.ForeignKey('Restaurant', on_delete=models.SET_NULL, null=True, blank=True)

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15)
    logo = models.ImageField(upload_to='restaurant_logos/', blank=True, null=True)

    def __str__(self):
        return self.name

class PaymentAccount(models.Model):
    ACCOUNT_TYPES = ( ('CBE', 'CBE'), ('Telebirr', 'Telebirr'), ('Awash', 'Awash'), ('Dashin', 'Dashin'), ('Other', 'Other'), )
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='payment_accounts')
    account_type = models.CharField(max_length=50, choices=ACCOUNT_TYPES)
    account_number = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.restaurant.name} - {self.account_type}"

class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='menu_images/')
    
    def __str__(self):
        return self.name
    
    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if not ratings.exists():
            return 0
        return sum(rating.stars for rating in ratings) / ratings.count()
    
    @property
    def rating_count(self):
        return self.ratings.count()

class Addon(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='addons')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='addon_images/', blank=True, null=True)
    def __str__(self):
        return f"{self.name} ({self.restaurant.name})"

# --- NEW MODEL FOR RATINGS ADDED HERE ---
class Rating(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='ratings')
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    stars = models.IntegerField() # 1 to 5
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.stars} stars for {self.menu_item.name} by {self.customer.username}"

def generate_order_code():
    return str(uuid.uuid4().hex[:8].upper())

class Order(models.Model):
    STATUS_CHOICES = ( ('Pending Payment', 'Pending Payment'), ('Pending Approval', 'Pending Approval'), ('Preparing', 'Preparing'), ('Ready for Pickup', 'Ready for Pickup'), ('Delivered', 'Delivered'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled'), )
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending Payment')
    payment_proof = models.ImageField(upload_to='payment_proofs/', blank=True, null=True)
    order_code = models.CharField(max_length=8, default=generate_order_code, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ready_for_pickup_at = models.DateTimeField(null=True, blank=True, help_text='When the order was marked as ready for pickup')
    
    def __str__(self):
        return f"Order {self.order_code} by {self.customer.username}"
    
    def should_auto_deliver(self):
        """Check if order should be automatically marked as delivered (2 hours after ready for pickup)"""
        if self.status != 'Ready for Pickup' or not self.ready_for_pickup_at:
            return False
        
        from django.utils import timezone
        from datetime import timedelta
        
        # Check if 2 hours have passed since ready_for_pickup_at
        two_hours_ago = timezone.now() - timedelta(hours=2)
        return self.ready_for_pickup_at <= two_hours_ago

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, null=True, blank=True)
    addon = models.ForeignKey(Addon, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    def __str__(self):
        if self.menu_item: return f"{self.quantity} of {self.menu_item.name}"
        if self.addon: return f"{self.quantity} of {self.addon.name} (Addon)"
        return "Invalid Order Item"

class Conversation(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    subject = models.CharField(max_length=255, default="General Inquiry")
    created_at = models.DateTimeField(auto_now_add=True)
    is_open = models.BooleanField(default=True)
    def __str__(self):
        return f"Chat with {self.customer.username}"

class ChatMessage(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Message from {self.sender.username}"

# --- Activity Log ---
class ActivityLog(models.Model):
    class ActionType(models.TextChoices):
        ORDER_APPROVED = 'ORDER_APPROVED', 'Order Approved'
        ORDER_DELIVERED = 'ORDER_DELIVERED', 'Order Delivered'

    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, help_text='The sub-admin who performed the action.')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=50, choices=ActionType.choices)
    details = models.TextField(blank=True, help_text='Extra details like customer name, order total, etc.')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action_type} by {self.actor} on {self.order}"