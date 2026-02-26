from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
import string
import random
from .models import ConsultantApplication, Consultation


@admin.register(ConsultantApplication)
class ConsultantApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'phone', 'specialization', 'experience_years', 'consultation_rate', 'status_display', 'submitted_at', 'resume_link', 'cv_link', 'approve_button', 'reject_button')
    list_filter = ('processed', 'rejected', 'specialization', 'submitted_at')
    search_fields = ('full_name', 'email', 'phone', 'specialization')
    readonly_fields = ('submitted_at', 'approved_by', 'approved_at', 'rejected_by', 'rejected_at')
    list_per_page = 25
    
    # Add custom CSS for better appearance
    class Media:
        css = {
            'all': ('admin/css/admin_styles.css',)
        }
    
    fieldsets = (
        (None, {
            'fields': ('user', 'full_name', 'email', 'phone', 'specialization', 'experience_years', 'consultation_rate', 'cover_letter')
        }),
        ('Files', {
            'fields': ('resume', 'cv')
        }),
        ('Status', {
            'fields': ('processed', 'rejected', 'rejection_reason', 'submitted_at')
        }),
        ('Approval Info', {
            'fields': ('approved_by', 'approved_at')
        }),
        ('Rejection Info', {
            'fields': ('rejected_by', 'rejected_at')
        }),
    )

    def resume_link(self, obj):
        if obj.resume:
            return format_html('<a href="{}" target="_blank">Download resume</a>', obj.resume.url)
        return '-'
    resume_link.short_description = 'Resume'

    def cv_link(self, obj):
        if obj.cv:
            return format_html('<a href="{}" target="_blank">Download CV</a>', obj.cv.url)
        return '-'
    cv_link.short_description = 'CV'

    def status_display(self, obj):
        """Display a colored status showing if consultant is visible in frontend"""
        if obj.rejected:
            return format_html('<span style="color: red; font-weight: bold;">Rejected</span>')
        elif obj.processed and obj.approved_at:
            return format_html('<span style="color: green; font-weight: bold;">✓ Active (Visible)</span>')
        elif obj.processed:
            return format_html('<span style="color: orange;">Processed</span>')
        else:
            return format_html('<span style="color: gray;">Pending</span>')
    status_display.short_description = 'Frontend Status'

    def approve_button(self, obj):
        if not obj.processed and not obj.rejected:
            return format_html(
                '<a class="button" style="background-color: #28a745; color: white; padding: 5px 10px; border-radius: 3px; text-decoration: none;" href="{}">Approve</a>',
                reverse('admin:approve_consultant_application', args=[obj.pk])
            )
        elif obj.processed:
            return "Approved"
        return ""
    approve_button.short_description = 'Approve'

    def reject_button(self, obj):
        if not obj.processed and not obj.rejected:
            return format_html(
                '<a class="button" style="background-color: #dc3545; color: white; padding: 5px 10px; border-radius: 3px; text-decoration: none;" href="{}">Reject</a>',
                reverse('admin:reject_consultant_application', args=[obj.pk])
            )
        elif obj.rejected:
            return "Rejected"
        return ""
    reject_button.short_description = 'Reject'

    actions = ['approve_applications', 'reject_applications']

    def approve_applications(self, request, queryset):
        """Admin action: mark selected applications processed and set user type to consultant."""
        approved = 0
        for app in queryset:
            if not app.processed and not app.rejected and app.user:
                user = app.user
                # Generate a new random password
                new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
                user.user_type = 'consultant'
                user.set_password(new_password)
                user.save()

                app.processed = True
                app.approved_by = request.user
                app.approved_at = timezone.now()
                app.save()

                # Send approval email with login details
                recipient = app.email or user.email
                if recipient:
                    try:
                        send_mail(
                            subject='Your Consultant Application Has Been Approved',
                            message=(f'Hi {app.full_name},\n\n'
                                     'Congratulations! Your application to become a consultant on Construction Hub has been approved.\n\n'
                                     'Please pay the consultant membership fee to complete your registration.\n\n'
                                     'Your login details are:\n'
                                     f'Username: {user.username}\n'
                                     f'Password: {new_password}\n\n'
                                     'Please log in and change your password immediately after your first login.\n\n'
                                     'Regards,\nConstruction Hub Team'),
                            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com'),
                            recipient_list=[recipient],
                            fail_silently=True,
                        )
                    except Exception:
                        pass
                approved += 1
        self.message_user(request, f"Approved {approved} application(s). Set user type to consultant and sent login details.")
    approve_applications.short_description = 'Approve selected consultant applications and set user type to consultant'

    def reject_applications(self, request, queryset):
        """Admin action: reject selected applications and send email notification."""
        rejected = 0
        for app in queryset:
            if not app.processed and not app.rejected:
                # Set rejection details
                app.rejected = True
                app.processed = True  # Mark as processed (rejected)
                app.rejected_by = request.user
                app.rejected_at = timezone.now()
                
                # Use default rejection reason if not provided
                if not app.rejection_reason:
                    app.rejection_reason = "Your application did not meet our current requirements. Please review your documents and apply again."
                app.save()

                # Send rejection email
                recipient = app.email
                if recipient:
                    try:
                        send_mail(
                            subject='Your Consultant Application Has Been Rejected',
                            message=(f'Dear {app.full_name},\n\n'
                                     'Thank you for your interest in becoming a consultant on Construction Hub.\n\n'
                                     'After careful review of your application, we regret to inform you that your application has been not approved at this time.\n\n'
                                     f'Reason: {app.rejection_reason}\n\n'
                                     'If you believe this is a mistake or would like to address the concerns, please contact us.\n\n'
                                     'You may submit a new application with improved documentation in the future.\n\n'
                                     'Best regards,\nConstruction Hub Team'),
                            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com'),
                            recipient_list=[recipient],
                            fail_silently=True,
                        )
                    except Exception:
                        pass
                rejected += 1
        self.message_user(request, f"Rejected {rejected} application(s). Applicants have been notified via email.")
    reject_applications.short_description = 'Reject selected consultant applications and send email notification'

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<int:application_id>/approve/', self.admin_site.admin_view(self.approve_application), name='approve_consultant_application'),
            path('<int:application_id>/reject/', self.admin_site.admin_view(self.reject_application), name='reject_consultant_application'),
        ]
        return custom_urls + urls

    def approve_application(self, request, application_id):
        from django.contrib import messages
        from django.shortcuts import redirect
        from apps.accounts.models import CustomUser

        app = self.get_object(request, application_id)
        if app and not app.processed and not app.rejected:
            user = app.user
            if not user:
                # Check if user with this email already exists
                existing_user = CustomUser.objects.filter(email=app.email).first()
                if existing_user:
                    user = existing_user
                    app.user = user
                    app.save()
                else:
                    # Create a new user account for the consultant
                    username = app.email.split('@')[0] + str(app.id)  # Generate unique username
                    new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
                    user = CustomUser.objects.create_user(
                        username=username,
                        email=app.email,
                        password=new_password,
                        user_type='consultant'
                    )
                    app.user = user
                    app.save()

            # Generate a new random password and set user type to consultant
            new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            user.user_type = 'consultant'
            user.set_password(new_password)
            user.save()

            app.processed = True
            app.approved_by = request.user
            app.approved_at = timezone.now()
            app.save()

            # Send approval email with login details
            recipient = app.email or user.email
            if recipient:
                try:
                    send_mail(
                        subject='Your Consultant Application Has Been Approved',
                        message=(f'Hi {app.full_name},\n\n'
                                 'Congratulations! Your application to become a consultant on Construction Hub has been approved.\n\n'
                                 'Please pay the consultant membership fee to complete your registration.\n\n'
                                 'Your login details are:\n'
                                 f'Username: {user.username}\n'
                                 f'Password: {new_password}\n\n'
                                 'Please log in and change your password immediately after your first login.\n\n'
                                 'Regards,\nConstruction Hub Team'),
                        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com'),
                        recipient_list=[recipient],
                        fail_silently=True,
                    )
                except Exception:
                    pass

            messages.success(request, f'Approved application for {app.full_name}.')
        else:
            messages.warning(request, 'Application already processed or not found.')

        return redirect('admin:consultations_consultantapplication_changelist')

    def reject_application(self, request, application_id):
        from django.contrib import messages
        from django.shortcuts import redirect, get_object_or_404

        app = get_object_or_404(ConsultantApplication, pk=application_id)
        
        if request.method == 'POST':
            # Get rejection reason from form
            rejection_reason = request.POST.get('rejection_reason', '').strip()
            if not rejection_reason:
                rejection_reason = "Your application did not meet our current requirements. Please review your documents and apply again."
            
            # Set rejection details
            app.rejected = True
            app.processed = True  # Mark as processed (rejected)
            app.rejected_by = request.user
            app.rejected_at = timezone.now()
            app.rejection_reason = rejection_reason
            app.save()

            # Send rejection email
            recipient = app.email
            if recipient:
                try:
                    send_mail(
                        subject='Your Consultant Application Has Been Rejected',
                        message=(f'Dear {app.full_name},\n\n'
                                 'Thank you for your interest in becoming a consultant on Construction Hub.\n\n'
                                 'After careful review of your application, we regret to inform you that your application has been not approved at this time.\n\n'
                                 f'Reason: {rejection_reason}\n\n'
                                 'If you believe this is a mistake or would like to address the concerns, please contact us.\n\n'
                                 'You may submit a new application with improved documentation in the future.\n\n'
                                 'Best regards,\nConstruction Hub Team'),
                        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com'),
                        recipient_list=[recipient],
                        fail_silently=True,
                    )
                except Exception:
                    pass

            messages.success(request, f'Rejected application for {app.full_name}. Applicant has been notified via email.')
            return redirect('admin:consultations_consultantapplication_changelist')

        # If GET request, just reject with default reason
        app.rejected = True
        app.processed = True
        app.rejected_by = request.user
        app.rejected_at = timezone.now()
        app.rejection_reason = "Your application did not meet our current requirements. Please review your documents and apply again."
        app.save()

        # Send rejection email
        recipient = app.email
        if recipient:
            try:
                send_mail(
                    subject='Your Consultant Application Has Been Rejected',
                    message=(f'Dear {app.full_name},\n\n'
                             'Thank you for your interest in becoming a consultant on Construction Hub.\n\n'
                             'After careful review of your application, we regret to inform you that your application has been not approved at this time.\n\n'
                             'Reason: Your application did not meet our current requirements. Please review your documents and apply again.\n\n'
                             'If you believe this is a mistake or would like to address the concerns, please contact us.\n\n'
                             'You may submit a new application with improved documentation in the future.\n\n'
                             'Best regards,\nConstruction Hub Team'),
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com'),
                    recipient_list=[recipient],
                    fail_silently=True,
                )
            except Exception:
                pass

        messages.success(request, f'Rejected application for {app.full_name}. Applicant has been notified via email.')
        return redirect('admin:consultations_consultantapplication_changelist')


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'supplier', 'consultant', 'date_requested', 'date_scheduled', 'status')
    list_filter = ('status', 'date_requested')
    search_fields = ('customer__username', 'supplier__name', 'consultant_name')
    readonly_fields = ('date_requested',)
    
    # Add custom CSS for better appearance
    class Media:
        css = {
            'all': ('admin/css/admin_styles.css',)
        }
