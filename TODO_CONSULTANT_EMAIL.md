# TODO: Make Consultant Booking Emails More Professional

## Task
Improve the professional appearance of emails sent by consultants to clients about consultation bookings.

## Current Issue
The current email sent by consultants looks unprofessional:
```
Dear Client,

date next monday at 12 noon this is the link

---
This email was sent by Victorjunior Munene from Construction Hub.
Consultant Email: victorjuniormunene94@gmail.com
```

## Plan

### 1. Improve Email Template in Backend (dashboard/views.py)
- Add a more structured email format with:
  - Proper greeting with client's name
  - Consultation details section
  - Professional formatting with spacing
  - Better footer with contact information

### 2. Improve Frontend Placeholder Text (consultant_dashboard.html)
- Add better placeholder text to guide consultants on what to include
- Provide example of a professional message format

## Files to Edit
1. construction-hub/apps/dashboard/views.py - Update email template
2. construction-hub/templates/dashboard/consultant_dashboard.html - Update placeholder text

## Status
- [ ] Update email template in dashboard/views.py
- [ ] Update placeholder text in consultant_dashboard.html
