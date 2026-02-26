# TODO: Improve Update Payment Status Section in Customer Dashboard

## Task
Make the "Update Payment Status" section in the customer dashboard more professional and user-friendly by adding an order selector dropdown.

## Plan
- [x] 1. Update customer_dashboard.html to add order selector dropdown
- [x] 2. Add JavaScript for auto-selecting order when M-Pesa message is pasted
- [x] 3. Show order details when an order is selected
- [x] 4. Improve overall professional appearance
- [x] 5. Update the view to handle the selected order (optional - view parses message automatically)

## Changes Made
1. Added pending orders context to the dashboard view (already existed)
2. Added order selector dropdown in the HTML form showing pending orders
3. Added order details display section showing product, quantity, amount, date, and status
4. Added JavaScript for:
   - Dynamic order selection from dropdown
   - Auto-detecting order number from M-Pesa message (format: Order-ORD-XXXXXXXXX)
   - Visual feedback when order is auto-detected
5. Maintained professional appearance with gradient styling and smooth transitions
