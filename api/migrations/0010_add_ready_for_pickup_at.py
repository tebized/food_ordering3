# Generated manually for adding ready_for_pickup_at field to Order model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_add_delivered_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='ready_for_pickup_at',
            field=models.DateTimeField(blank=True, help_text='When the order was marked as ready for pickup', null=True),
        ),
    ]
