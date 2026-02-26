# Generated manually for adding order_image field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_alter_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_image',
            field=models.ImageField(blank=True, help_text='Image uploaded by supplier when creating order', null=True, upload_to='order_images/'),
        ),
    ]
