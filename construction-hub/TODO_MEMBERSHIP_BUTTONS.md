# TODO: Make Consultant and Supplier Membership Buttons Functional

## Status: COMPLETED

### Steps Completed:
1. [x] Fix pricing.html - Replace hardcoded href="#" with proper Django template tags
   - Consultant "Apply Now" button now links to {% url 'accounts:consultant_application' %}
   - Supplier "Become a Supplier" button now links to {% url 'accounts:register' %}?role=supplier

2. [x] Update register view to handle role query parameter
   - Added initial_role = request.GET.get('role', 'customer') in register view
   - Form is now initialized with the role from query parameter

3. [x] Update register.html template to pre-select role from query parameter
   - Added custom radio button styling for role selection
   - Role is pre-selected based on initial_role context variable

### Steps Pending:
- [ ] Create membership/subscription models (optional enhancement)
- [ ] Create membership payment flow (optional enhancement)
- [ ] Test the buttons
