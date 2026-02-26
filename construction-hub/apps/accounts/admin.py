from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import format_html
from django.utils import timezone
from .models import CustomUser, ContactMessage, Customer, ArchitecturalPlan, PlanPurchase
from allauth.socialaccount.models import SocialApp, SocialAccount, SocialToken
from allauth.socialaccount.admin import SocialAppAdmin, SocialAccountAdmin, SocialTokenAdmin


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'is_active', 'date_joined')
    list_filter = ('user_type', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone_number', 'company_name', 'location')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone_number', 'company_name', 'location')}),
    )
    
    # Add custom CSS for better appearance
    class Media:
        css = {
            'all': ('admin/css/admin_styles.css',)
        }


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'submitted_at', 'is_read', 'is_replied')
    list_filter = ('is_read', 'is_replied', 'submitted_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'submitted_at')
    ordering = ('-submitted_at',)
    
    # Add custom CSS for better appearance
    class Media:
        css = {
            'all': ('admin/css/admin_styles.css',)
        }
    
    fieldsets = (
        ('📬 Message Details', {
            'fields': ('name', 'email', 'subject', 'message', 'submitted_at', 'is_read'),
            'classes': ('message-details',)
        }),
        ('✉️ Admin Reply', {
            'fields': ('admin_reply', 'replied_at', 'is_replied'),
            'classes': ('admin-reply',)
        }),
    )
    
    # Actions for bulk operations
    actions = ['mark_as_read', 'mark_as_replied']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f"{queryset.count()} message(s) marked as read.")
    mark_as_read.short_description = "Mark selected messages as read"
    
    def mark_as_replied(self, request, queryset):
        queryset.update(is_replied=True, replied_at=timezone.now())
        self.message_user(request, f"{queryset.count()} message(s) marked as replied.")
    mark_as_replied.short_description = "Mark selected messages as replied"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return True
    
    def save_model(self, request, obj, form, change):
        # Check if this is a new reply or an update to existing reply
        if obj.admin_reply:
            # Get the original message to compare
            if change:
                # This is an update - get the original object
                try:
                    original = ContactMessage.objects.get(pk=obj.pk)
                    original_reply = original.admin_reply
                except ContactMessage.DoesNotExist:
                    original_reply = ''
            else:
                original_reply = ''
            
            # If this is a new reply or the reply has changed, send email
            if not original_reply or original_reply != obj.admin_reply:
                obj.replied_at = timezone.now()
                obj.is_replied = True
                
                # Send reply email to customer
                self._send_reply_email(obj)
        
        super().save_model(request, obj, form, change)
    
    def _send_reply_email(self, obj):
        """Send reply email to the customer"""
        try:
            subject = f"Re: {obj.subject}" if obj.subject else "Reply to your message"
            
            # Build the email message
            message = f"""Hello {obj.name},

Thank you for contacting us. Here is our reply to your message:

Your original message:
{obj.message}

Our reply:
{obj.admin_reply}

Best regards,
Construction Hub Team
"""
            
            # Send email
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@constructionhub.com',
                recipient_list=[obj.email],
                fail_silently=False,
            )
            print(f"Reply email sent to {obj.email}")
        except Exception as e:
            print(f"Error sending email: {e}")


# Register Social Account models in admin
# Note: SocialApp, SocialAccount, and SocialToken are already registered by allauth
# admin.site.register(SocialApp, SocialAppAdmin)
# admin.site.register(SocialAccount, SocialAccountAdmin)
# admin.site.register(SocialToken, SocialTokenAdmin)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'user_email')
    search_fields = ('user__username', 'user__email')
    raw_id_fields = ('user',)
    
    def user_email(self, obj):
        return obj.user.email if obj.user else '-'
    user_email.short_description = 'Email'


@admin.register(ArchitecturalPlan)
class ArchitecturalPlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'plan_type', 'price', 'is_active', 'has_file', 'created_at')
    list_filter = ('plan_type', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('is_active',)
    ordering = ('-created_at',)
    
    def has_file(self, obj):
        if obj.plan_file:
            return format_html('<span style="color: green;">✓ File uploaded</span>')
        return format_html('<span style="color: red;">✗ No file</span>')
    has_file.short_description = 'Plan File'
    
    fieldsets = (
        (None, {
            'fields': ('name', 'plan_type', 'price', 'description', 'features')
        }),
        ('File', {
            'fields': ('plan_file',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(PlanPurchase)
class PlanPurchaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'purchase_number', 'customer', 'plan', 'amount', 'status', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('purchase_number', 'customer__username', 'customer_name', 'customer_phone')
    readonly_fields = ('purchase_number', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Customer Info', {
            'fields': ('customer', 'customer_name', 'customer_phone')
        }),
        ('Plan Info', {
            'fields': ('plan', 'amount')
        }),
        ('Purchase Details', {
            'fields': ('purchase_number', 'status', 'created_at', 'updated_at')
        }),
        ('Payment Info', {
            'fields': ('mpesa_phone_number', 'mpesa_transaction_id', 'mpesa_checkout_request_id', 'payment_status', 'payment_initiated_at', 'payment_completed_at')
        }),
    )
