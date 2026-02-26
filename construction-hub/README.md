# Construction Hub

## Overview
Construction Hub is a web application designed to connect customers with suppliers of construction products. The platform allows customers to order materials, consult about building plans and costs, and receive planning services. 

## Features
- **User Roles**: The application supports three user roles: Admin, Customers, and Suppliers.
- **Supplier Functionality**: Suppliers can post construction materials, including costs and locations.
- **Customer Functionality**: Customers can view products, make orders, apply for consultations, and manage their dashboards.
- **Consultation Services**: Customers can request consultations regarding building plans and costs.

## Project Setup

### Prerequisites
- Python 3.x
- Django
- PostgreSQL (or any other database of your choice)

### Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   cd construction-hub
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up your environment variables:
   - Copy `.env.example` to `.env` and fill in the required values.

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

7. Start the development server:
   ```
   python manage.py runserver
   ```

## Directory Structure
```
construction-hub/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── Dockerfile
├── construction_hub/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── accounts/
│   ├── suppliers/
│   ├── products/
│   ├── orders/
│   ├── consultations/
│   └── dashboard/
├── templates/
├── static/
├── docs/
└── tests/
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.