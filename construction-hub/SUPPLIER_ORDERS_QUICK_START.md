# 🎯 SUPPLIER ORDER MANAGEMENT - QUICK START GUIDE

## What's New?

Suppliers can now:
1. **Create** orders for customers
2. **View** all orders they've created in a dedicated dashboard section
3. **Edit** order details (quantity, customer info, status)
4. **Delete** orders they've created
5. **Download** PDF receipts for any order

## Access the Feature

### Step 1: Login
- Go to: http://127.0.0.1:8000/accounts/dashboard/
- Login with supplier credentials
- Example: `supplier1` / `supplier1`

### Step 2: View Your Created Orders
- Look for the section: **"Orders You Created"**
- You'll see up to 5 of your most recent orders
- Each order shows:
  - Order number (ORD-XXXXXXXX)
  - Product name
  - Quantity ordered
  - Customer details (name, phone, location)
  - Order status (Saved, Paid, Shipped, Completed)
  - Total cost in KSH

## How to Use

### Creating a New Order
1. Click the **"+ Create New Order"** button
2. Select a product from your inventory
3. Enter customer details:
   - Customer name
   - Phone number
   - Location
4. Enter quantity
5. Click "Create Order"
6. Order appears in your "Orders You Created" section

### Editing an Order
1. Find the order in "Orders You Created" section
2. Click the **"Edit"** button (blue button)
3. Modify any of these fields:
   - **Quantity** - Change how many units
   - **Customer Name** - Update customer name
   - **Customer Phone** - Update phone number
   - **Customer Location** - Update delivery location
   - **Order Status** - Change status (Saved → Paid → Shipped → Completed)
4. Click **"Save Changes"**
5. Dashboard updates automatically

### Downloading a Receipt
1. Find the order in your dashboard
2. Click the **"Receipt"** button (blue button)
3. PDF downloads automatically
4. Receipt includes:
   - Order number and date
   - Product details
   - Quantity and pricing
   - Customer information
   - Total cost

### Deleting an Order
1. Find the order in "Orders You Created" section
2. Click the **"Delete"** button (red button)
3. Review the confirmation page showing all order details
4. Click **"Yes, Delete This Order"** to confirm
5. Order is permanently removed

⚠️ **Note:** Deletion is permanent and cannot be undone!

## Dashboard Overview

### Section 1: "Orders You Created"
- **Purpose:** Manage orders you created for customers
- **Actions Available:** Edit, Receipt, Delete
- **Shows:** 5 most recent orders
- **Status:** Can edit and delete

### Section 2: "Incoming Orders"
- **Purpose:** View orders customers placed for your products
- **Actions Available:** Download receipt only
- **Shows:** Orders placed by customers
- **Status:** Read-only (customer manages these)

## Sample Orders

Pre-loaded sample orders for testing:

| Order # | Customer | Product | Quantity | Status |
|---------|----------|---------|----------|--------|
| ORD-00000023 | John Mwangi | Cement | 5 | Saved |
| ORD-00000024 | Mary Kimani | Steel Rebars | 10 | Saved |
| ORD-00000025 | David Kipchoge | Cement | 15 | Saved |
| ORD-00000026 | Grace Njoki | Steel Rebars | 20 | Saved |
| ORD-00000027 | Peter Kariuki | Cement | 25 | Saved |

Try editing or deleting these to test the feature!

## Keyboard Shortcuts & Tips

### Navigation
- Dashboard: `http://127.0.0.1:8000/accounts/dashboard/`
- Create Order: `http://127.0.0.1:8000/suppliers/create-order/`
- Direct Edit: `http://127.0.0.1:8000/orders/{ID}/edit-supplier/`
- Direct Delete: `http://127.0.0.1:8000/orders/{ID}/delete-supplier/`

### Tips
- **Bulk Creation:** Create multiple orders in sequence from "Create New Order" button
- **Status Updates:** Update order status as you fulfill them (Saved → Paid → Shipped → Completed)
- **Receipt Archiving:** Download receipts regularly for your records
- **Edit Before Payment:** Edit details before marking order as "Paid"
- **Quantity Adjustment:** Easily adjust quantities if customer changes their order

## Troubleshooting

### "You do not have permission to edit this order"
- **Cause:** You're trying to edit someone else's order or an order linked to a product you don't own
- **Solution:** Only view/edit your own orders. Check if the product belongs to your supplier account.

### "Order not found"
- **Cause:** Order ID doesn't exist or has been deleted
- **Solution:** Refresh the dashboard and verify the order number.

### Receipt won't download
- **Cause:** Browser popup blocker may be active
- **Solution:** Allow popups for this site or try right-clicking the Receipt button

### Edit form shows validation errors
- **Cause:** Missing required field or invalid format
- **Solution:** Check all fields are filled:
  - Customer Name (required)
  - Phone Number (required, 10-15 digits)
  - Location (required)
  - Quantity (required, must be positive number)

## Security Notes

✅ **Your Data is Protected:**
- Only you can edit/delete your orders
- Login required for all operations
- All changes are tracked with timestamps

🔒 **Best Practices:**
- Don't share your login credentials
- Log out when finished (especially on shared computers)
- Regularly download receipts for important orders
- Review your orders before deleting

## FAQ

**Q: Can I create an order for the same customer multiple times?**
A: Yes! You can create unlimited orders. The system tracks them separately.

**Q: What happens if I delete an order?**
A: It's permanently removed from your system. You can't recover deleted orders, but their PDF receipt remains if you downloaded it.

**Q: Can I change which product is in an order?**
A: No, the product is fixed once created. If you need a different product, create a new order.

**Q: Can customers see the orders I create for them?**
A: No, supplier-created orders are only visible in your dashboard. They don't appear in customer dashboards.

**Q: How do I change order status from "Saved" to "Paid"?**
A: Click Edit on the order, change the Status dropdown to "Paid", then click Save Changes.

**Q: Can I see who created each order (me vs customer)?**
A: Yes! Orders in "Orders You Created" are ones you created. Orders in "Incoming Orders" are customer-created.

## Contact & Support

For issues or feature requests:
1. Check the dashboard for error messages
2. Review this guide for solutions
3. Contact system administrator if problems persist

---

## Version Info
- **Feature:** Supplier Order Management v1.0
- **Last Updated:** January 26, 2026
- **Status:** ✅ Production Ready

Happy order managing! 📦
