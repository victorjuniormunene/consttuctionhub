# Generated manually for plan_type field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0010_order_mpesa_checkout_request_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='plan_type',
            field=models.CharField(blank=True, help_text='Type of architectural plan purchased (2_bedroom, 3_bedroom)', max_length=50, null=True),
        ),
    ]
