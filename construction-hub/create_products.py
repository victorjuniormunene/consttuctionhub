import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from apps.suppliers.models import Product
from apps.suppliers.models import Supplier
from apps.accounts.models import CustomUser

# Create or get a supplier user
user, user_created = CustomUser.objects.get_or_create(
    username='supplier1',
    defaults={
        'email': 'supplier1@example.com',
        'user_type': 'supplier'
    }
)

# Get or create a supplier profile
supplier, created = Supplier.objects.get_or_create(
    user=user,
    defaults={'company_name': 'Sample Supplier'}
)

# Create sample products
products = [
    {
        'name': 'Cement',
        'description': 'High-quality cement for construction',
        'cost': 850.00,
        'supplier': supplier,
        'image_url': '/static/images/simba cement.jpg'
    },
    {
        'name': 'Steel Rebars',
        'description': 'Durable steel rebars for reinforcement',
        'cost': 2200.00,
        'supplier': supplier,
        'image_url': '/static/images/Steel-Rebars.jpg'
    },
    {
        'name': 'Bricks',
        'description': 'Red clay bricks for building walls',
        'cost': 45.00,
        'supplier': supplier,
        'image_url': '/static/images/bricks.jpg'
    },
    {
        'name': 'Sand',
        'description': 'Fine construction sand',
        'cost': 5500.00,
        'supplier': supplier,
        'image_url': '/static/images/sand.jpg'
    },
    {
        'name': 'Gravel',
        'description': 'Construction gravel for foundations',
        'cost': 1400.00,
        'supplier': supplier,
        'image_url': '/static/images/Gravel.jpg'
    },
    {
        'name': 'Concrete Blocks',
        'description': 'Lightweight concrete blocks for walls',
        'cost': 1100.00,
        'supplier': supplier,
        'image_url': '/static/images/bricks.jpg'
    },
    {
        'name': 'Wood Planks',
        'description': 'Pressure-treated wood planks for framing',
        'cost': 1600.00,
        'supplier': supplier,
        'image_url': '/static/images/timber.jpg'
    },
    {
        'name': 'Roofing Tiles',
        'description': 'Clay roofing tiles for residential buildings',
        'cost': 850.00,
        'supplier': supplier,
        'image_url': '/static/images/roofing.jpg'
    },
    {
        'name': 'PVC Pipes',
        'description': 'Durable PVC pipes for plumbing',
        'cost': 1250.00,
        'supplier': supplier,
        'image_url': '/static/images/construction team.jpg'
    },
    {
        'name': 'Paint',
        'description': 'Interior and exterior paint for finishing',
        'cost': 2600.00,
        'supplier': supplier,
        'image_url': '/static/images/construction team.jpg'
    },
    {
        'name': 'Glass Windows',
        'description': 'Double-glazed glass windows for buildings',
        'cost': 13500.00,
        'supplier': supplier,
        'image_url': '/static/images/construction team.jpg'
    },
    {
        'name': 'Steel Beams',
        'description': 'Structural steel beams for large constructions',
        'cost': 10500.00,
        'supplier': supplier,
        'image_url': '/static/images/mabati.jpg'
    },
    {
        'name': 'Insulation Foam',
        'description': 'Thermal insulation foam for energy efficiency',
        'cost': 1850.00,
        'supplier': supplier,
        'image_url': '/static/images/roofing.jpg'
    },
    {
        'name': 'Nails and Screws',
        'description': 'Assorted nails and screws for fastening',
        'cost': 950.00,
        'supplier': supplier,
        'image_url': '/static/images/timber.jpg'
    }
]

for product_data in products:
    product, created = Product.objects.get_or_create(
        name=product_data['name'],
        defaults=product_data
    )
    if not created:
        product.cost = product_data['cost']
        product.save()

print(f"Updated or created {len(products)} sample products")
