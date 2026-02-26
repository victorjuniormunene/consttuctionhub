# Order Management & Supplier Dashboard Guide

## Overview

Your construction hub project has a fully functional order management system that allows suppliers to create orders and track them in the supplier dashboard. Orders are automatically linked to suppliers through their products.

---

## How Orders Work

### 1. **Order Creation**

Orders can be created in two ways:

#### **Option A: Customer Creates Order (Public)**
- Navigate to `/orders/create/`
- Select a product from any supplier
- Enter customer details (name, phone, location)
- Enter quantity
- System automatically deducts stock from the product's `available_quantity`
- Order status: `saved` → `paid` → `shipped` → `completed`

#### **Option B: Supplier Creates Order (For Their Customers)**
- Navigate to `/suppliers/create-order/` (Supplier Dashboard → "+ Create Order" button)
- Select one of YOUR supplier products only
- Enter customer information
- System creates order directly with you as the creator
- Order is immediately visible in your Supplier Dashboard

### 2. **Order Model Structure**

```python
Order
├── customer (ForeignKey to User - optional)
├── product (ForeignKey to Product)
├── quantity (PositiveInteger)
├── price (DecimalField - captured at order time)
├── order_number (Auto-generated: ORD-XXXXXXXX)
├── customer_name (CharField)
├── customer_number (CharField - phone)
├── customer_location (CharField - address)
├── created_at (DateTime)
├── updated_at (DateTime)
└── status (CharField with choices):
    - saved (Initial state)
    - paid (Payment received)
    - shipped (Item sent)
    - completed (Order fulfilled)
    - canceled (Order cancelled)
```

### 3. **Supplier Dashboard Orders Section**

**Location:** `/accounts/dashboard/` (for suppliers)

**Features:**
- ✅ **View All Orders**: Display all orders for your products
- ✅ **Filter by Status**: 
  - Pending (saved + paid status)
  - Shipped
  - Completed
  - Canceled
- ✅ **Order Cards Display**:
  - Product name
  - Order ID
  - Current status badge
  - Customer information (name, phone, location)
  - Quantity and total cost (KSH)
  - Created timestamp
  - Action buttons

**Action Buttons for Each Order:**
1. **View Details** → Full order details page
2. **📥 Receipt** → Download PDF receipt
3. **Mark Shipped** (if pending) → Update status to "shipped"
4. **Mark Completed** (if shipped) → Update status to "completed"

**Bulk Action:**
- **"Sell All Pending Orders"** button → Marks all pending orders as completed at once

---

## Step-by-Step: Creating an Order as a Supplier

### Step 1: Access Order Creation
1. Log in as a supplier
2. Go to **Supplier Dashboard** (`/accounts/dashboard/`)
3. Click **"+ Create Order"** button (top right of Incoming Orders section)

### Step 2: Fill Order Form
```
Form Fields:
├── Select Product (Required) - Your products only
├── Quantity (Required) - Number of units
├── Customer Name (Required) - Client's full name
├── Customer Phone (Required) - Client's phone number
└── Customer Location (Required) - Delivery address
```

### Step 3: Submit
- Click **"Create Order"** button
- System shows success message
- Redirects to dashboard
- Order now appears in "Incoming Orders" section

---

## Step-by-Step: Managing Orders in Dashboard

### View Incoming Orders
1. Open **Supplier Dashboard**
2. Scroll to **"Incoming Orders"** section
3. Use filter dropdown to view by status:
   - All orders
   - Pending (count shown)
   - Shipped (count shown)
   - Completed (count shown)
   - Canceled (count shown)

### Update Order Status
1. Find the order in the dashboard
2. Click appropriate action button:
   - **"Mark Shipped"** → Status changes to "shipped"
   - **"Mark Completed"** → Status changes to "completed"

### View Order Details
1. Click **"View Details"** on any order card
2. See full order information
3. Download receipt or perform status updates

### Download Receipt
1. Click **"📥 Receipt"** button on order card
2. PDF file downloads with:
   - Order number
   - Product details
   - Customer information
   - Quantity and total cost
   - Payment details
   - Company information (if supplier has company_name set)

---

## Order Status Flow

```
saved (Initial)
  ↓
paid (Payment confirmed)
  ↓
shipped (Item dispatched)
  ↓
completed (Delivered & fulfilled)

OR at any stage → canceled (If needed)
```

**Who Controls Status:**
- Suppliers manage status through their dashboard
- Status reflects fulfillment progress
- Orders start as "saved" automatically

---

## How Orders Connect to Suppliers

### Automatic Linking
```
Product → Supplier (ForeignKey)
   ↓
Order → Product (ForeignKey)
   ↓
Order automatically tied to Product's Supplier
```

### Display Logic
When a supplier views their dashboard:
```python
# Backend filters orders like this:
supplier_orders = Order.objects.filter(product__supplier=supplier)
```

**Result:** Only orders for products you created appear in your dashboard!

---

## Key Features Implemented

### ✅ Stock Management
- Orders automatically deduct from product `available_quantity`
- Stock check prevents overselling
- Uses database transactions for accuracy

### ✅ Order Numbering
- Auto-generated format: `ORD-00000001`
- Unique per order
- Human-readable for customers

### ✅ Price Capture
- Price stored at time of order
- Uses product cost if not specified
- Prevents price changes affecting old orders

### ✅ Customer Information
- Optional customer user account link
- Manual name/phone/location entry
- Supports anonymous orders

### ✅ Email Notifications
- Supplier notified when new order created
- Uses Django email backend (console for development)
- Can be configured for real email

### ✅ Filtering & Stats
- Quick filter by status
- Count badges show pending/shipped/completed totals
- Shows order count in dashboard

### ✅ PDF Receipts
- Download receipt for any order
- Professional formatting
- Includes all order details

---

## URL Reference

| Action | URL | Method |
|--------|-----|--------|
| Create Order (Public) | `/orders/create/` | GET/POST |
| View My Orders | `/orders/` | GET |
| Create Order (Supplier) | `/suppliers/create-order/` | GET/POST |
| View Order Details | `/orders/<order_id>/` | GET |
| Supplier Dashboard | `/accounts/dashboard/` | GET |
| Download Receipt | `/consultations/download-order-receipt-supplier/<order_id>/` | GET |
| Mark as Shipped | `/suppliers/orders/<order_id>/?action=mark_shipped` | GET |
| Mark as Completed | `/suppliers/orders/<order_id>/?action=mark_completed` | GET |
| Sell All Orders | `/suppliers/sell-all-orders/` | POST |

---

## Testing the Order System

### Test Case 1: Create Public Order
1. Log in as customer
2. Go to `/orders/create/`
3. Select any product
4. Enter details and submit
5. ✅ Order appears in customer dashboard AND supplier's dashboard

### Test Case 2: Supplier Creates Order
1. Log in as supplier
2. Go to `/accounts/dashboard/`
3. Click "+ Create Order"
4. Fill form with your product
5. Submit
6. ✅ Order appears in your dashboard

### Test Case 3: Update Order Status
1. In Supplier Dashboard
2. Find a pending order
3. Click "Mark Shipped"
4. ✅ Status badge changes to "Shipped" (cyan)
5. Click "Mark Completed"
6. ✅ Status badge changes to "Completed" (green)

### Test Case 4: Filter Orders
1. In Supplier Dashboard
2. Use filter dropdown
3. Select "Pending" or other status
4. ✅ Dashboard shows only orders with that status
5. Counter updates

---

## Customization Options

### Add More Order Statuses
Edit [apps/orders/models.py](apps/orders/models.py#L16):
```python
status = models.CharField(max_length=20, choices=[
    ('saved', 'Saved'),
    ('paid', 'Paid'),
    ('shipped', 'Shipped'),
    ('completed', 'Completed'),
    ('canceled', 'Canceled'),
    # Add new ones here:
    ('processing', 'Processing'),
    ('quality_check', 'Quality Check'),
], default='saved')
```

### Change Order Number Format
Edit [apps/orders/models.py](apps/orders/models.py#L36):
```python
# Current: ORD-00000001
# Try: f"SO-{self.created_at.strftime('%Y%m%d')}-{self.pk:05d}"
# Result: SO-20260126-00001
```

### Add Additional Order Fields
Edit [apps/orders/models.py](apps/orders/models.py):
```python
# Add to Order model:
notes = models.TextField(blank=True)
delivery_date = models.DateField(null=True, blank=True)
priority = models.CharField(max_length=20, choices=[
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
], default='medium')
```

---

## Database Queries

### Get All Orders for a Supplier
```python
from apps.suppliers.models import Supplier
from apps.orders.models import Order

supplier = Supplier.objects.get(user=request.user)
orders = Order.objects.filter(product__supplier=supplier)
```

### Get Orders by Status
```python
pending = Order.objects.filter(product__supplier=supplier, status='saved')
shipped = Order.objects.filter(product__supplier=supplier, status='shipped')
completed = Order.objects.filter(product__supplier=supplier, status='completed')
```

### Get Total Revenue per Supplier
```python
from django.db.models import Sum

total = Order.objects.filter(
    product__supplier=supplier,
    status='completed'
).aggregate(Sum('total_cost'))['total_cost__sum']
```

---

## Troubleshooting

### Order Not Appearing in Dashboard
- ✅ Check: Is the product created by this supplier?
- ✅ Check: Is the user marked as a supplier (has Supplier profile)?
- ✅ Check: Is the order linked to the correct product?

### Stock Not Updating
- ✅ Check: Product's `available_quantity` value
- ✅ Check: Order created successfully (no error messages)
- ✅ Check: Stock was positive before order

### Status Won't Update
- ✅ Check: Are you the supplier of that product?
- ✅ Check: Is the order status currently "saved" or "shipped"?

### Receipt Not Downloading
- ✅ Check: pdf_utils.py is configured correctly
- ✅ Check: ReportLab is installed (`pip install reportlab`)

---

## Related Files

- **Models:** [apps/orders/models.py](apps/orders/models.py)
- **Views:** [apps/orders/views.py](apps/orders/views.py)
- **Supplier Views:** [apps/suppliers/views.py](apps/suppliers/views.py)
- **Dashboard Template:** [templates/dashboard/supplier_dashboard.html](templates/dashboard/supplier_dashboard.html)
- **Order Creation Template:** [templates/suppliers/supplier_create_order.html](templates/suppliers/supplier_create_order.html)
- **Forms:** [apps/orders/forms.py](apps/orders/forms.py)

---

## Summary

Your project has a **complete, production-ready order management system** with:
- ✅ Order creation (public + supplier-specific)
- ✅ Stock management with atomic transactions
- ✅ Status tracking and filtering
- ✅ PDF receipt generation
- ✅ Email notifications
- ✅ Clean supplier dashboard UI
- ✅ Bulk order operations

**To use it:**
1. Create products as a supplier
2. Click "+ Create Order" in dashboard
3. Fill in customer details
4. Track order status with action buttons
5. Download receipts as needed

The system is ready to use! 🚀
