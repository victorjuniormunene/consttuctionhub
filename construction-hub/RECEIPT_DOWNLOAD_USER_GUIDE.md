# Receipt Download Feature - User Guide

## For Customers

### How to Download an Order Receipt

#### Method 1: After Placing an Order
1. **Fill the order form** with your details:
   - Quantity
   - Your name
   - Phone number
   - Location/address

2. **Submit the order** - You'll see a confirmation page

3. **Click "Download Receipt"** button
   - This downloads your order receipt as a PDF
   - File name: `receipt_ORD-XXXXXXXX.pdf`
   - Contains all order details and supplier information

#### Method 2: From Your Dashboard
1. **Go to Dashboard** (`/accounts/dashboard/`)
2. **Find your order** in the orders list
3. **Click "Download Receipt"** next to the order
4. PDF will be saved to your downloads folder

### What's in Your Receipt?
- ✓ Unique order number (e.g., ORD-00000001)
- ✓ Order date and time
- ✓ Product name and quantity
- ✓ Unit price and total cost in KSH
- ✓ Your contact information
- ✓ Supplier details and contact info
- ✓ Order status

### Payment Instructions
1. After submitting order, click **"Proceed to Payment"**
2. You'll see:
   - M-Pesa payment number
   - Amount to pay (in KSH)
   - Instructions
3. Send exact amount via M-Pesa
4. Click **"I Have Made the Payment"** to confirm
5. Order status changes to "Paid"
6. Supplier is notified automatically

---

## For Suppliers

### How to Download Order Receipts

#### View All Orders
1. **Go to Dashboard** (`/accounts/dashboard/`)
2. **Check "Supplier Orders"** section
3. Shows all orders placed for your products

#### Download Receipt
1. Find the order in your dashboard
2. Click the order to view details
3. Click **"Download Receipt"** button
4. PDF will be saved with format: `receipt_ORD-XXXXXXXX.pdf`

### Receipt Information
You can see:
- ✓ Customer's complete information
- ✓ Product ordered and quantity
- ✓ Payment amount
- ✓ Order number for easy reference
- ✓ Customer's location
- ✓ Order status and dates

### Email Notifications
You receive automatic emails for:
- ✓ **New Order**: When customer places order
- ✓ **Payment Received**: When customer pays via M-Pesa

Click the links in emails to download receipts directly.

---

## Technical Details

### Receipt File Format
- **Format**: PDF (Adobe Portable Document Format)
- **Size**: ~2.5 KB per receipt
- **Quality**: Professional print-ready
- **Pages**: Single page, all details on one page

### Receipt Access URLs
```
# Download receipt for order #5
GET /orders/5/receipt/download/

# Shows order confirmation page with download option
GET /order-confirmation/5/
```

### Order Number Format
- Format: `ORD-XXXXXXXX`
- Example: `ORD-00000001`, `ORD-00000015`, `ORD-00000020`
- Unique for each order
- Printed on receipt and in confirmation page

---

## Troubleshooting

### Receipt won't download
**Problem**: Clicking download does nothing
**Solution**: 
- Make sure you're logged in
- Try a different browser
- Check if pop-ups are blocked

### Wrong order number showing
**Problem**: Receipt shows ID instead of order number
**Solution**: 
- This is automatic - order numbers are generated as ORD-XXXXXXXX
- If showing old format, refresh the page

### Can't find my receipt
**Problem**: Lost the receipt link
**Solution**:
1. Go to your Dashboard
2. Find the order in the list
3. Click "Download Receipt" again

### Technical Issues
- Check that all orders have been properly saved
- Verify order numbers are in format: `ORD-XXXXXXXX`
- Ensure you're accessing correct order URL

---

## Important Information

### Privacy & Security
- Only you and the supplier can access your receipt
- Receipts are downloaded directly - no email storage
- Customer data on receipt is only visible to relevant parties

### Keeping Records
- **Download immediately** after order
- **Store safely** on your computer
- **Keep for records** (recommended 1-2 years)
- **Print if needed** - PDF is print-ready

### Order Status
- **Saved**: Order created, not yet paid
- **Pending**: Waiting for payment
- **Paid**: Payment received
- **Shipped**: Order on the way
- **Completed**: Order delivered
- **Canceled**: Order cancelled

Check the receipt for current status at time of download.

---

## Quick Links

- **Browse Products**: `/suppliers/products/`
- **Place Order**: `/orders/create/`
- **Dashboard**: `/accounts/dashboard/`
- **View Order**: `/orders/<order-id>/`
- **Download Receipt**: `/orders/<order-id>/receipt/download/`

---

## Need Help?

If you encounter issues:
1. Clear your browser cache
2. Try a different browser
3. Contact the supplier directly using info on the receipt
4. Report technical issues to the support team

**Last Updated**: January 26, 2026
