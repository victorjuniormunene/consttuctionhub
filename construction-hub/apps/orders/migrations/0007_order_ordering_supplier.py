# Generated manually for adding ordering_supplier field

from django.db import migrations, models
import django.conf


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_order_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='ordering_supplier',
            field=models.ForeignKey(blank=True, help_text='Supplier who created this order', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='supplier_orders', to='accounts.customuser'),
        ),
    ]
