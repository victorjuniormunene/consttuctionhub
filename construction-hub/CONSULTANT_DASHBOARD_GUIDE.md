# Consultant Dashboard - Complete Feature Guide

## Dashboard Overview

The Consultant Dashboard (`/dashboard/consultant/`) provides a comprehensive management interface for approved consultants to track all customer interactions, pending work, and business metrics.

---

## Dashboard Sections

### 1. Welcome Header
```
Welcome back, [username]!
Manage your consultations, customer details, and pending orders.
```

---

### 2. Statistics Dashboard (4-Card Grid)

#### Card 1: Total Consultations
- **Icon**: 📋
- **Data**: Count of all assigned consultations
- **Example**: "12 Total Consultations"

#### Card 2: Pending Consultations
- **Icon**: ⏳
- **Data**: Count of pending (not yet started) consultations
- **Example**: "3 Pending Consultations"

#### Card 3: Completed Consultations
- **Icon**: ✅
- **Data**: Count of finished consultations
- **Example**: "8 Completed Consultations"

#### Card 4: Pending Orders
- **Icon**: 📦
- **Data**: Count of orders in 'saved' or 'paid' status
- **Example**: "5 Pending Orders"

---

### 3. Pending Issues & Orders Section (NEW)

**Description**: Master table showing all action items requiring consultant attention.

#### Table Columns

| Column | Content | Details |
|--------|---------|---------|
| **Type** | Consultation or Order badge | Color-coded (blue for consultation, purple for order) |
| **Customer** | Customer info | Username + Email |
| **Details** | Item information | Consultation text, Project name, or Product name + quantity |
| **Date** | When created/requested | Formatted as "M d, Y" (e.g., "Jan 26, 2026") |
| **Status** | Current status | Colored badge (Yellow for pending, Green for paid) |
| **Action** | Quick link | "View Details" or "View Order" link |

#### Consultation Row Example
```
Type:      [Consultation - blue badge]
Customer:  john_smith
           john@example.com
Details:   I need advice on cement selection for my project...
           Project: ABC Concrete Suppliers
Date:      Jan 25, 2026
Status:    [PENDING - yellow badge]
Action:    View Details
```

#### Order Row Example
```
Type:      [Order - purple badge]
Customer:  jane_doe
           +254 712345678
Details:   Reinforced Steel Bars (50 units)
           Order #ORD-00000001
           📍 Nairobi, Westlands
Date:      Jan 24, 2026
Status:    [PAID - green badge]
Action:    View Order
```

#### Empty State
When no pending consultations or orders:
```
✨
All caught up!
No pending consultations or orders at the moment.
```

---

### 4. Customer Details & Activity Section (NEW)

**Description**: Comprehensive cards for each customer with full interaction history.

#### Customer Card Structure

```
┌─────────────────────────────────────────┐
│ 👤 Customer Name                        │
│                                         │
│ Email: john@example.com                │
│ Username: john_doe                      │
│ Role: [CUSTOMER - badge]               │
│                                         │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│ 📋 Active Consultations (2)            │
│                                         │
│ ┌──────────────────────────────────┐  │
│ │ ABC Construction Supplies        │  │
│ │ Status: Scheduled | Jan 25       │  │
│ └──────────────────────────────────┘  │
│                                         │
│ ┌──────────────────────────────────┐  │
│ │ XYZ Materials Inc                │  │
│ │ Status: Pending | Jan 24         │  │
│ └──────────────────────────────────┘  │
│                                         │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│ 📦 Orders (3)                          │
│                                         │
│ ┌──────────────────────────────────┐  │
│ │ Cement (20 units)                │  │
│ │ Order #ORD-00000001 | Paid       │  │
│ │ Total: $500.00                   │  │
│ └──────────────────────────────────┘  │
│                                         │
│ [✉️ Email] [View Profile]             │
└─────────────────────────────────────────┘
```

#### Customer Card Elements

1. **Header**
   - Customer name (or username if name not available)
   - Profile icon (👤)

2. **Contact Information**
   - Email address (clickable mailto link)
   - Username
   - Role badge

3. **Active Consultations Subsection**
   - Shows all consultations with this consultant
   - Displays company name
   - Shows status and request date
   - Blue left border indicator

4. **Orders Subsection**
   - Lists all customer orders
   - Shows product name and quantity
   - Displays order number and status
   - Shows total cost
   - Purple left border indicator

5. **Quick Actions**
   - Email button (sends to customer's email)
   - View Profile button

#### Empty Customer State
```
👥
No customers yet
Customer details will appear here once you have assigned consultations or orders.
```

---

### 5. Recent Consultations Section

**Description**: Timeline view of the 5 most recent consultations.

#### Consultation Item Structure

```
┌──────────────────────────────────────────┐
│ Customer: john_smith                    │
│ Project: ABC Concrete Suppliers         │
│ Status: Pending • Jan 25, 2026          │
│                                          │
│ Details:                                │
│ I need technical advice on cement       │
│ selection for my commercial project...  │
│                                          │
│ [PENDING] [View Details] [Start]       │
└──────────────────────────────────────────┘
```

#### Features
- Truncates long details to visible preview
- Color-coded status badges (Yellow=Pending, Green=Completed, Blue=Scheduled)
- Quick action buttons contextual based on status
- Shows "View All" link if more than 5 consultations exist

---

### 6. Quick Actions Section (3-Card Grid)

#### Card 1: Update Profile
- **Icon**: 📝
- **Title**: Update Profile
- **Description**: Keep your consultant profile current
- **Button**: Edit Profile → `/accounts/consultant-application/`

#### Card 2: My Products
- **Icon**: 💼
- **Title**: My Products
- **Description**: Manage your product catalog
- **Button**: View Products → `/accounts/dashboard/`

#### Card 3: Support
- **Icon**: 📞
- **Title**: Support
- **Description**: Get help from our support team
- **Button**: Contact Support → `/accounts/contact/`

---

## Data Context Variables

The template receives the following context from the view:

```python
{
    # Consultations
    'assigned_consultations': QuerySet of all assigned consultations,
    'pending_consultations': QuerySet of pending consultations,
    'consultations': All assigned consultations (for backward compatibility),
    'total_assigned': Integer count of total consultations,
    'pending_count': Integer count of pending consultations,
    'completed_count': Integer count of completed consultations,
    
    # Orders
    'pending_orders': QuerySet of pending orders (status in ['saved', 'paid']),
    'pending_orders_count': Integer count of pending orders,
    
    # User & Supplier
    'supplier': Supplier instance for current consultant,
    'customers': QuerySet of all customers interacting with this consultant,
    
    # Request
    'request.user': Current logged-in consultant user,
}
```

---

## Styling Details

### Colors Used
- **Primary Blue**: #1976d2 (buttons, links)
- **Success Green**: #28a745 (completed items)
- **Warning Yellow**: #ffc107 (pending items)
- **Info Blue**: #0d6efd (information)
- **Purple**: #7b1fa2 (orders)
- **Text**: #333 (dark text)
- **Light Text**: #666 (secondary text)
- **Background**: #fafafa (light gray)

### Typography
- **Headers** (h2): 2rem font size, bold
- **Subheaders** (h3): 1.1rem font size
- **Labels** (h4): 1rem font size
- **Body**: 0.95rem default
- **Small text**: 0.85rem

### Responsive Design
- **Desktop**: 1fr 1fr grid for sections
- **Tablet**: Single column with full width
- **Mobile**: Full width, responsive cards

---

## Interaction Flows

### View Pending Consultation
1. Consultant opens dashboard
2. Sees pending item in "Pending Issues & Orders" table
3. Clicks "View Details" link
4. Opens consultation details page

### View Pending Order
1. Consultant views "Pending Issues & Orders" table
2. Clicks "View Order" link
3. Opens order detail page with full information

### Contact Customer
1. Consultant scrolls to "Customer Details" section
2. Finds customer card
3. Clicks "Email" button
4. Opens email client with pre-filled recipient

### Update Profile
1. Consultant clicks "Update Profile" in Quick Actions
2. Navigates to consultant application form
3. Updates qualifications, specialization, files
4. Saves changes

---

## Access Control

- **Required Authentication**: Yes (login required)
- **Required Role**: Consultant (must have approved Supplier profile)
- **Permission Check**: Automatic - non-consultants redirected with error message
- **Error Message**: "You must be an approved consultant (Supplier profile) to access the consultant dashboard."

---

## Browser Compatibility

- **Chrome**: ✅ Full support
- **Firefox**: ✅ Full support
- **Safari**: ✅ Full support
- **Edge**: ✅ Full support
- **Mobile Safari**: ✅ Responsive
- **Chrome Mobile**: ✅ Responsive

---

## Performance Considerations

### Database Queries Optimized
- Uses `prefetch_related()` for customer orders and consultations
- Single query for assigned consultations
- Filtered pending orders by supplier

### Rendering Performance
- Shows first 5 consultations, loads rest on demand
- Truncates long text to prevent layout shift
- CSS Grid for responsive layout

---

## Status Color Reference

| Status | Color | Meaning |
|--------|-------|---------|
| Pending | Yellow (#fff3cd) | Awaiting action |
| Scheduled | Blue (#cfe2ff) | Appointment set |
| Completed | Green (#d4edda) | Work finished |
| Paid | Green (#e8f5e9) | Payment received |
| Saved | Yellow (#fff3cd) | Draft/Awaiting |

---

## Example Dashboard Scenarios

### Scenario 1: New Consultant with No Activity
- Statistics show all zeros
- "Pending Issues" section shows "All caught up!"
- "Customer Details" section shows "No customers yet"
- Prompted to update profile and accept consultations

### Scenario 2: Busy Consultant
- Multiple pending items in table
- Several customer cards with active consultations
- Quick actions readily available for common tasks
- Dashboard provides at-a-glance status

### Scenario 3: Consultant Reviewing Customer History
1. Opens consultant dashboard
2. Finds customer in "Customer Details" section
3. Views all active consultations with that customer
4. Reviews all orders from that customer
5. Clicks email to reach out
6. Uses action buttons for next steps

---

## Tips for Consultants

1. **Check Pending Items Daily**: Review the "Pending Issues & Orders" table each morning
2. **Contact Inactive Customers**: Use email buttons in customer cards to follow up
3. **Update Your Profile**: Keep qualifications and experience current
4. **Track Completions**: Monitor the "Completed Consultations" count for performance
5. **Manage Products**: Keep product catalog updated via "My Products" link

---

## Support Resources

- **Dashboard Help**: View "Quick Actions" section
- **Contact Admin**: Use "Support" button
- **Report Issues**: Send via contact form
- **Email Admin**: kaje@constructionhub.local
