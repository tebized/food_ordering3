# Generated manually for adding Delivered status to Order model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_activitylog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(
                choices=[
                    ('Pending Payment', 'Pending Payment'),
                    ('Pending Approval', 'Pending Approval'),
                    ('Preparing', 'Preparing'),
                    ('Ready for Pickup', 'Ready for Pickup'),
                    ('Delivered', 'Delivered'),
                    ('Completed', 'Completed'),
                    ('Cancelled', 'Cancelled'),
                ],
                default='Pending Payment',
                max_length=20
            ),
        ),
    ]
