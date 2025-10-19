from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import Order


class Command(BaseCommand):
    help = 'Automatically mark orders as delivered after 2 hours if user has not confirmed delivery'

    def handle(self, *args, **options):
        # Find orders that are "Ready for Pickup" and should be auto-delivered
        orders_to_auto_deliver = Order.objects.filter(
            status='Ready for Pickup',
            ready_for_pickup_at__isnull=False
        )
        
        auto_delivered_count = 0
        
        for order in orders_to_auto_deliver:
            if order.should_auto_deliver():
                order.status = 'Delivered'
                order.save()
                auto_delivered_count += 1
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Auto-delivered order {order.order_code} (customer: {order.customer.username})'
                    )
                )
        
        if auto_delivered_count == 0:
            self.stdout.write(
                self.style.SUCCESS('No orders needed auto-delivery')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully auto-delivered {auto_delivered_count} order(s)'
                )
            )
