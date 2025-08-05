from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from django.utils import timezone
from .models import IPO, IPOTracking, IPONotification, IPOReminder, IPOApplication, ContactMessage
from .serializers import IPOSerializer
from django.views.decorators.http import require_POST

import csv
import io
from datetime import datetime
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.utils.html import strip_tags

# Admin check function
def is_admin(user):
    return user.is_authenticated and user.is_staff

# Home View - Redirects to login
def home_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('ipo_app:admin_dashboard')
        else:
            return redirect('ipo_app:user_dashboard')
    return redirect('ipo_app:login')

# Web Views - Read-only for regular users
class IPOListView(ListView):
    model = IPO
    template_name = 'ipo_app/ipo_list.html'
    context_object_name = 'ipos'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = IPO.objects.all()
        status = self.request.GET.get('status')
        search = self.request.GET.get('search')
        
        if status:
            queryset = queryset.filter(status=status)
        
        if search:
            queryset = queryset.filter(company_name__icontains=search)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upcoming_ipos'] = IPO.objects.filter(status='upcoming')
        context['ongoing_ipos'] = IPO.objects.filter(status='ongoing')
        context['listed_ipos'] = IPO.objects.filter(status='listed')
        # Add count data for navbar badges
        context['total_upcoming'] = IPO.objects.filter(status='upcoming').count()
        context['total_ongoing'] = IPO.objects.filter(status='ongoing').count()
        context['total_listed'] = IPO.objects.filter(status='listed').count()
        context['total_all'] = IPO.objects.count()
        # Add admin status for template
        context['is_admin'] = self.request.user.is_authenticated and self.request.user.is_staff
        return context

class IPODetailView(DetailView):
    model = IPO
    template_name = 'ipo_app/ipo_detail.html'
    context_object_name = 'ipo'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin'] = self.request.user.is_authenticated and self.request.user.is_staff
        return context

# Admin-only IPO Management Views
@login_required
@user_passes_test(is_admin)
def ipo_create(request):
    if request.method == 'POST':
        try:
            # Create new IPO
            ipo = IPO.objects.create(
                company_name=request.POST.get('company_name'),
                price_band=request.POST.get('price_band'),
                open_date=request.POST.get('open_date'),
                close_date=request.POST.get('close_date'),
                issue_size=request.POST.get('issue_size'),
                issue_type=request.POST.get('issue_type'),
                status=request.POST.get('status'),
                ipo_price=request.POST.get('ipo_price') or None,
                listing_price=request.POST.get('listing_price') or None,
                current_market_price=request.POST.get('current_market_price') or None,
                listing_date=request.POST.get('listing_date') or None,
            )
            
            # Handle file uploads
            if 'logo' in request.FILES:
                ipo.logo = request.FILES['logo']
            if 'rhp_pdf' in request.FILES:
                ipo.rhp_pdf = request.FILES['rhp_pdf']
            if 'drhp_pdf' in request.FILES:
                ipo.drhp_pdf = request.FILES['drhp_pdf']
            
            ipo.save()
            messages.success(request, 'IPO created successfully!')
            return redirect('ipo_app:admin_dashboard')
        except Exception as e:
            messages.error(request, f'Error creating IPO: {str(e)}')
    
    return render(request, 'ipo_app/ipo_form.html')

@login_required
@user_passes_test(is_admin)
def ipo_update(request, pk):
    ipo = get_object_or_404(IPO, pk=pk)
    if request.method == 'POST':
        try:
            # Update IPO fields
            ipo.company_name = request.POST.get('company_name')
            ipo.price_band = request.POST.get('price_band')
            ipo.open_date = request.POST.get('open_date')
            ipo.close_date = request.POST.get('close_date')
            ipo.issue_size = request.POST.get('issue_size')
            ipo.issue_type = request.POST.get('issue_type')
            ipo.status = request.POST.get('status')
            ipo.ipo_price = request.POST.get('ipo_price') or None
            ipo.listing_price = request.POST.get('listing_price') or None
            ipo.current_market_price = request.POST.get('current_market_price') or None
            ipo.listing_date = request.POST.get('listing_date') or None
            
            # Handle file uploads
            if 'logo' in request.FILES:
                ipo.logo = request.FILES['logo']
            if 'rhp_pdf' in request.FILES:
                ipo.rhp_pdf = request.FILES['rhp_pdf']
            if 'drhp_pdf' in request.FILES:
                ipo.drhp_pdf = request.FILES['drhp_pdf']
            
            ipo.save()
            messages.success(request, 'IPO updated successfully!')
            return redirect('ipo_app:admin_dashboard')
        except Exception as e:
            messages.error(request, f'Error updating IPO: {str(e)}')
    
    return render(request, 'ipo_app/ipo_form.html', {'ipo': ipo})

@login_required
@user_passes_test(is_admin)
def ipo_delete(request, pk):
    ipo = get_object_or_404(IPO, pk=pk)
    if request.method == 'POST':
        try:
            company_name = ipo.company_name
            ipo.delete()
            messages.success(request, f'IPO "{company_name}" deleted successfully!')
            return redirect('ipo_app:admin_dashboard')
        except Exception as e:
            messages.error(request, f'Error deleting IPO: {str(e)}')
    
    return render(request, 'ipo_app/ipo_confirm_delete.html', {'ipo': ipo})

# Authentication Views
def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('ipo_app:admin_dashboard')
        else:
            return redirect('ipo_app:user_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            if user.is_staff:
                return redirect('ipo_app:admin_dashboard')
            else:
                return redirect('ipo_app:user_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'ipo_app/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('ipo_app:login')

# User Dashboard Views
@login_required
def user_dashboard(request):
    if request.user.is_staff:
        return redirect('ipo_app:admin_dashboard')
    
    # Get user-specific data
    upcoming_ipos = IPO.objects.filter(status='upcoming')[:6]
    ongoing_ipos = IPO.objects.filter(status='ongoing')[:6]
    listed_ipos = IPO.objects.filter(status='listed')[:6]
    
    # Notifications (latest 5)
    notifications = IPONotification.objects.filter(user=request.user).order_by('-created_at')[:5]
    notifications_count = IPONotification.objects.filter(user=request.user).count()
    
    # Tracked IPOs
    tracked_ipos = IPOTracking.objects.filter(user=request.user).select_related('ipo')
    tracked_ipos_count = tracked_ipos.count()
    
    # Applications
    applications_count = IPOApplication.objects.filter(user=request.user).count()
    
    # Active reminders
    active_reminders = IPOReminder.objects.filter(user=request.user, is_active=True).order_by('reminder_date')
    reminders_count = active_reminders.count()
    
    # Recent applications
    recent_applications = IPOApplication.objects.filter(user=request.user).select_related('ipo').order_by('-application_date')[:5]
    
    context = {
        'upcoming_ipos': upcoming_ipos,
        'ongoing_ipos': ongoing_ipos,
        'listed_ipos': listed_ipos,
        'total_upcoming': IPO.objects.filter(status='upcoming').count(),
        'total_ongoing': IPO.objects.filter(status='ongoing').count(),
        'total_listed': IPO.objects.filter(status='listed').count(),
        'total_all': IPO.objects.count(),
        'notifications': notifications,
        'notifications_count': notifications_count,
        'tracked_ipos': tracked_ipos,
        'tracked_ipos_count': tracked_ipos_count,
        'applications_count': applications_count,
        'reminders_count': reminders_count,
        'active_reminders': active_reminders,
        'recent_applications': recent_applications,
    }
    
    return render(request, 'ipo_app/user_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def send_notification(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        user_id = request.POST.get('user_id')
        if user_id:
            user = User.objects.get(pk=user_id)
            IPONotification.objects.create(user=user, message=message)
        else:
            for user in User.objects.all():
                IPONotification.objects.create(user=user, message=message)
        messages.success(request, 'Notification sent!')
    return redirect('ipo_app:admin_dashboard')

# Admin Dashboard Views
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Get admin-specific data
    ipos = IPO.objects.all().order_by('-created_at')
    upcoming_count = IPO.objects.filter(status='upcoming').count()
    ongoing_count = IPO.objects.filter(status='ongoing').count()
    listed_count = IPO.objects.filter(status='listed').count()
    total_count = IPO.objects.count()
    all_users = User.objects.all()
    
    # Get additional data for dashboard
    total_users = User.objects.count()
    total_applications = IPOApplication.objects.count()
    total_tracking = IPOTracking.objects.count()
    total_reminders = IPOReminder.objects.count()
    recent_ipos = IPO.objects.all().order_by('-created_at')[:5]
    
    context = {
        'ipos': ipos,
        'upcoming_count': upcoming_count,
        'ongoing_count': ongoing_count,
        'listed_count': listed_count,
        'total_count': total_count,
        'total_ipos': total_count,
        'ongoing_ipos': ongoing_count,
        'total_users': total_users,
        'total_applications': total_applications,
        'total_tracking': total_tracking,
        'total_reminders': total_reminders,
        'recent_ipos': recent_ipos,
        # Add navbar data
        'total_upcoming': upcoming_count,
        'total_ongoing': ongoing_count,
        'total_listed': listed_count,
        'total_all': total_count,
        'all_users': all_users,
    }
    return render(request, 'ipo_app/admin_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def bulk_import_ipos(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        skip_duplicates = request.POST.get('skip_duplicates') == 'on'
        validate_data = request.POST.get('validate_data') == 'on'
        
        if not csv_file:
            messages.error(request, 'Please select a CSV file.')
            return redirect('ipo_app:bulk_import')
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a valid CSV file.')
            return redirect('ipo_app:bulk_import')
        
        try:
            # Read CSV file
            decoded_file = csv_file.read().decode('utf-8')
            csv_data = csv.DictReader(io.StringIO(decoded_file))
            
            imported_count = 0
            skipped_count = 0
            error_count = 0
            errors = []
            
            for row_num, row in enumerate(csv_data, start=2):  # Start from 2 to account for header
                try:
                    # Validate required fields
                    if not row.get('company_name'):
                        raise ValidationError(f"Row {row_num}: Company name is required")
                    
                    if not row.get('issue_type'):
                        raise ValidationError(f"Row {row_num}: Issue type is required")
                    
                    if not row.get('status'):
                        raise ValidationError(f"Row {row_num}: Status is required")
                    
                    # Check for duplicates if skip_duplicates is enabled
                    if skip_duplicates and IPO.objects.filter(company_name=row['company_name']).exists():
                        skipped_count += 1
                        continue
                    
                    # Parse dates
                    open_date = None
                    close_date = None
                    listing_date = None
                    
                    if row.get('open_date'):
                        try:
                            open_date = datetime.strptime(row['open_date'], '%Y-%m-%d').date()
                        except ValueError:
                            raise ValidationError(f"Row {row_num}: Invalid open_date format. Use YYYY-MM-DD")
                    
                    if row.get('close_date'):
                        try:
                            close_date = datetime.strptime(row['close_date'], '%Y-%m-%d').date()
                        except ValueError:
                            raise ValidationError(f"Row {row_num}: Invalid close_date format. Use YYYY-MM-DD")
                    
                    if row.get('listing_date'):
                        try:
                            listing_date = datetime.strptime(row['listing_date'], '%Y-%m-%d').date()
                        except ValueError:
                            raise ValidationError(f"Row {row_num}: Invalid listing_date format. Use YYYY-MM-DD")
                    
                    # Parse fields
                    issue_size = row.get('issue_size', '')
                    price_band = row.get('price_band', '')
                    
                    ipo_price = None
                    if row.get('ipo_price') and row['ipo_price'].strip():
                        try:
                            ipo_price = float(row['ipo_price'])
                        except ValueError:
                            raise ValidationError(f"Row {row_num}: Invalid ipo_price. Must be a number")
                    
                    listing_price = None
                    if row.get('listing_price') and row['listing_price'].strip():
                        try:
                            listing_price = float(row['listing_price'])
                        except ValueError:
                            raise ValidationError(f"Row {row_num}: Invalid listing_price. Must be a number")
                    
                    current_market_price = None
                    if row.get('current_market_price') and row['current_market_price'].strip():
                        try:
                            current_market_price = float(row['current_market_price'])
                        except ValueError:
                            raise ValidationError(f"Row {row_num}: Invalid current_market_price. Must be a number")
                    
                    # Validate status
                    valid_statuses = ['upcoming', 'ongoing', 'listed']
                    if row['status'].lower() not in valid_statuses:
                        raise ValidationError(f"Row {row_num}: Invalid status. Must be one of: {', '.join(valid_statuses)}")
                    
                    # Validate issue type
                    valid_issue_types = ['Book Built Issue', 'Fixed Price Issue', 'SME IPO']
                    if row['issue_type'] not in valid_issue_types:
                        raise ValidationError(f"Row {row_num}: Invalid issue_type. Must be one of: {', '.join(valid_issue_types)}")
                    
                    # Create IPO object
                    ipo = IPO(
                        company_name=row['company_name'],
                        issue_type=row['issue_type'],
                        price_band=price_band,
                        issue_size=issue_size,
                        open_date=open_date,
                        close_date=close_date,
                        listing_date=listing_date,
                        status=row['status'].lower(),
                        ipo_price=ipo_price,
                        listing_price=listing_price,
                        current_market_price=current_market_price
                    )
                    
                    # Validate the model
                    if validate_data:
                        ipo.full_clean()
                    
                    ipo.save()
                    imported_count += 1
                    
                except ValidationError as e:
                    error_count += 1
                    errors.append(str(e))
                except Exception as e:
                    error_count += 1
                    errors.append(f"Row {row_num}: Unexpected error - {str(e)}")
            
            # Prepare success/error messages
            if imported_count > 0:
                success_msg = f"Successfully imported {imported_count} IPOs."
                if skipped_count > 0:
                    success_msg += f" Skipped {skipped_count} duplicates."
                if error_count > 0:
                    success_msg += f" {error_count} rows had errors."
                messages.success(request, success_msg)
            
            if errors:
                error_msg = "Import completed with errors:\n" + "\n".join(errors[:5])  # Show first 5 errors
                if len(errors) > 5:
                    error_msg += f"\n... and {len(errors) - 5} more errors."
                messages.warning(request, error_msg)
            
            if imported_count == 0 and error_count > 0:
                messages.error(request, f"No IPOs were imported. {error_count} errors occurred.")
            
        except Exception as e:
            messages.error(request, f'Error processing CSV file: {str(e)}')
        
        return redirect('ipo_app:bulk_import')
    
    return render(request, 'ipo_app/bulk_import.html')

# API Views - Admin only
class IPOViewSet(viewsets.ModelViewSet):
    queryset = IPO.objects.all()
    serializer_class = IPOSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['company_name']
    ordering_fields = ['open_date', 'close_date', 'listing_date', 'company_name']
    ordering = ['-open_date']
    
    def get_permissions(self):
        # Only admin users can access API
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return []
        return []
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        ipos = self.queryset.filter(status='upcoming')
        serializer = self.get_serializer(ipos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def ongoing(self, request):
        ipos = self.queryset.filter(status='ongoing')
        serializer = self.get_serializer(ipos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def listed(self, request):
        ipos = self.queryset.filter(status='listed')
        serializer = self.get_serializer(ipos, many=True)
        return Response(serializer.data)

@login_required
@require_POST
def track_ipo(request, pk):
    ipo = get_object_or_404(IPO, pk=pk)
    IPOTracking.objects.get_or_create(user=request.user, ipo=ipo)
    # Optionally, add a notification
    IPONotification.objects.create(user=request.user, message=f'You started tracking {ipo.company_name}')
    messages.success(request, f'IPO "{ipo.company_name}" added to your tracked IPOs.')
    return redirect('ipo_app:user_dashboard')

@login_required
def track_performance(request, pk):
    ipo = get_object_or_404(IPO, pk=pk)
    if ipo.status != 'listed':
        messages.warning(request, 'Performance tracking is only available for listed IPOs.')
        return redirect('ipo_app:ipo_detail', pk=pk)
    
    # Calculate performance metrics
    performance_data = {
        'ipo': ipo,
        'listing_gain': ipo.listing_gain,
        'current_return': ipo.current_return,
        'days_since_listing': (timezone.now().date() - ipo.listing_date).days if ipo.listing_date else None,
        'price_change': ipo.current_market_price - ipo.listing_price if ipo.current_market_price and ipo.listing_price else None,
        'total_return': ((ipo.current_market_price - ipo.ipo_price) / ipo.ipo_price * 100) if ipo.current_market_price and ipo.ipo_price else None,
        'abs_listing_gain': abs(ipo.listing_gain) if ipo.listing_gain else None,
        'abs_current_return': abs(ipo.current_return) if ipo.current_return else None,
    }
    
    return render(request, 'ipo_app/track_performance.html', performance_data)

@login_required
def mark_notification_read(request, notification_id):
    notif = get_object_or_404(IPONotification, pk=notification_id, user=request.user)
    notif.is_read = True
    notif.save()
    return redirect('ipo_app:user_dashboard')

@login_required
def all_notifications(request):
    notifications = IPONotification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'ipo_app/all_notifications.html', {'notifications': notifications})

@login_required
@user_passes_test(is_admin)
def export_ipos_csv(request):
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Build queryset with filters
    queryset = IPO.objects.all()
    
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    if date_from:
        queryset = queryset.filter(open_date__gte=date_from)
    
    if date_to:
        queryset = queryset.filter(open_date__lte=date_to)
    
    # Create response
    response = HttpResponse(content_type='text/csv')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"ipo_data_export_{timestamp}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Create CSV writer
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'Company Name',
        'Issue Type', 
        'Price Band (Lower)',
        'Price Band (Upper)',
        'Issue Size (Cr)',
        'Lot Size',
        'Open Date',
        'Close Date',
        'Listing Date',
        'Status',
        'IPO Price',
        'Listing Price',
        'Current Market Price',
        'Gain/Loss (%)',
        'Total Applications',
        'Subscription Rate',
        'Created Date',
        'Last Updated'
    ])
    
    # Write data rows
    for ipo in queryset.order_by('-open_date'):
        # Calculate gain/loss percentage
        gain_loss = 0
        if ipo.ipo_price and ipo.current_market_price:
            gain_loss = ((ipo.current_market_price - ipo.ipo_price) / ipo.ipo_price) * 100
        
        # Get total applications for this IPO
        total_applications = IPOApplication.objects.filter(ipo=ipo).count()
        
        writer.writerow([
            ipo.company_name,
            ipo.issue_type,
            ipo.price_band_lower,
            ipo.price_band_upper,
            ipo.issue_size,
            ipo.lot_size,
            ipo.open_date.strftime('%Y-%m-%d') if ipo.open_date else '',
            ipo.close_date.strftime('%Y-%m-%d') if ipo.close_date else '',
            ipo.listing_date.strftime('%Y-%m-%d') if ipo.listing_date else '',
            ipo.status.title(),
            ipo.ipo_price or '',
            ipo.listing_price or '',
            ipo.current_market_price or '',
            f"{gain_loss:.2f}%" if gain_loss != 0 else '',
            total_applications,
            ipo.subscription_rate or '',
            ipo.created_at.strftime('%Y-%m-%d %H:%M:%S') if ipo.created_at else '',
            ipo.updated_at.strftime('%Y-%m-%d %H:%M:%S') if ipo.updated_at else ''
        ])
    
    return response

@login_required
@user_passes_test(is_admin)
def analytics_dashboard(request):
    from django.db.models import Avg, Count, Sum, Q
    from datetime import datetime, timedelta
    import json
    
    # Basic counts
    total_ipos = IPO.objects.count()
    upcoming_count = IPO.objects.filter(status='upcoming').count()
    ongoing_count = IPO.objects.filter(status='ongoing').count()
    listed_count = IPO.objects.filter(status='listed').count()
    
    # Calculate percentages
    total = total_ipos if total_ipos > 0 else 1
    upcoming_percentage = (upcoming_count / total) * 100
    ongoing_percentage = (ongoing_count / total) * 100
    listed_percentage = (listed_count / total) * 100
    
    # Financial statistics
    avg_ipo_price = IPO.objects.exclude(ipo_price=None).aggregate(avg=Avg('ipo_price'))['avg']
    avg_listing_price = IPO.objects.exclude(listing_price=None).aggregate(avg=Avg('listing_price'))['avg']
    total_issue_size = IPO.objects.aggregate(total=Sum('issue_size'))['total'] or 0
    avg_issue_size = IPO.objects.aggregate(avg=Avg('issue_size'))['avg'] or 0
    
    # Application statistics
    total_applications = IPOApplication.objects.count()
    avg_applications_per_ipo = total_applications / total if total > 0 else 0
    
    # Performance statistics
    listed_ipos = IPO.objects.filter(status='listed').exclude(ipo_price=None).exclude(current_market_price=None)
    avg_gain_loss = 0
    if listed_ipos.exists():
        total_gain_loss = 0
        for ipo in listed_ipos:
            if ipo.ipo_price and ipo.current_market_price:
                gain_loss = ((ipo.current_market_price - ipo.ipo_price) / ipo.ipo_price) * 100
                total_gain_loss += gain_loss
        avg_gain_loss = total_gain_loss / listed_ipos.count()
    
    # Top performers
    top_performers = []
    for ipo in IPO.objects.filter(status='listed').exclude(ipo_price=None).exclude(current_market_price=None)[:10]:
        gain_loss = 0
        if ipo.ipo_price and ipo.current_market_price:
            gain_loss = ((ipo.current_market_price - ipo.ipo_price) / ipo.ipo_price) * 100
        
        application_count = IPOApplication.objects.filter(ipo=ipo).count()
        
        top_performers.append({
            'id': ipo.id,
            'company_name': ipo.company_name,
            'issue_size': ipo.issue_size,
            'ipo_price': ipo.ipo_price,
            'current_market_price': ipo.current_market_price,
            'gain_loss': gain_loss,
            'application_count': application_count
        })
    
    # Sort by gain/loss
    top_performers.sort(key=lambda x: x['gain_loss'], reverse=True)
    
    # Monthly trend data
    monthly_data = []
    monthly_labels = []
    for i in range(6):
        date = datetime.now() - timedelta(days=30*i)
        month_start = date.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        count = IPO.objects.filter(
            created_at__gte=month_start,
            created_at__lte=month_end
        ).count()
        
        monthly_data.append(count)
        monthly_labels.append(date.strftime('%b %Y'))
    
    monthly_data.reverse()
    monthly_labels.reverse()
    
    # Issue size distribution
    small_ipos = IPO.objects.filter(issue_size__lt=100).count()
    medium_ipos = IPO.objects.filter(issue_size__gte=100, issue_size__lt=500).count()
    large_ipos = IPO.objects.filter(issue_size__gte=500, issue_size__lt=1000).count()
    mega_ipos = IPO.objects.filter(issue_size__gte=1000).count()
    
    issue_size_data = [small_ipos, medium_ipos, large_ipos, mega_ipos]
    
    # Performance vs Issue Size scatter data
    performance_data = []
    for ipo in IPO.objects.filter(status='listed').exclude(ipo_price=None).exclude(current_market_price=None):
        gain_loss = 0
        if ipo.ipo_price and ipo.current_market_price:
            gain_loss = ((ipo.current_market_price - ipo.ipo_price) / ipo.ipo_price) * 100
        
        performance_data.append({
            'x': ipo.issue_size or 0,
            'y': gain_loss
        })
    
    # Additional statistics
    max_subscription_rate = 0  # Placeholder since subscription_rate field doesn't exist
    
    # Most popular IPO (by applications)
    most_popular_ipo = None
    if IPOApplication.objects.exists():
        popular_ipo = IPOApplication.objects.values('ipo__company_name').annotate(
            count=Count('id')
        ).order_by('-count').first()
        if popular_ipo:
            most_popular_ipo = popular_ipo['ipo__company_name']
    
    # User statistics
    active_users = User.objects.filter(is_active=True).count()
    user_growth = 0  # Placeholder for user growth calculation
    
    # Growth rate calculation
    current_month = datetime.now().month
    current_year = datetime.now().year
    last_month = current_month - 1 if current_month > 1 else 12
    last_year = current_year if current_month > 1 else current_year - 1
    
    current_month_ipos = IPO.objects.filter(
        created_at__year=current_year,
        created_at__month=current_month
    ).count()
    
    last_month_ipos = IPO.objects.filter(
        created_at__year=last_year,
        created_at__month=last_month
    ).count()
    
    growth_rate = 0
    if last_month_ipos > 0:
        growth_rate = ((current_month_ipos - last_month_ipos) / last_month_ipos) * 100
    
    context = {
        'total_ipos': total_ipos,
        'upcoming_count': upcoming_count,
        'ongoing_count': ongoing_count,
        'listed_count': listed_count,
        'upcoming_percentage': upcoming_percentage,
        'ongoing_percentage': ongoing_percentage,
        'listed_percentage': listed_percentage,
        'avg_ipo_price': avg_ipo_price,
        'avg_listing_price': avg_listing_price,
        'total_issue_size': total_issue_size,
        'avg_issue_size': avg_issue_size,
        'total_applications': total_applications,
        'avg_applications_per_ipo': avg_applications_per_ipo,
        'avg_gain_loss': avg_gain_loss,
        'top_performers': top_performers,
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_data': json.dumps(monthly_data),
        'issue_size_data': json.dumps(issue_size_data),
        'performance_data': json.dumps(performance_data),
        'max_subscription_rate': max_subscription_rate,
        'most_popular_ipo': most_popular_ipo,
        'active_users': active_users,
        'user_growth': user_growth,
        'growth_rate': growth_rate,
    }
    
    return render(request, 'ipo_app/analytics.html', context)

@login_required
def set_reminder(request, ipo_id):
    ipo = get_object_or_404(IPO, pk=ipo_id)
    if request.method == 'POST':
        reminder_date = request.POST.get('reminder_date')
        reminder_time = request.POST.get('reminder_time')
        message = request.POST.get('message', '')
        
        reminder, created = IPOReminder.objects.get_or_create(
            user=request.user,
            ipo=ipo,
            defaults={
                'reminder_date': reminder_date,
                'reminder_time': reminder_time,
                'message': message
            }
        )
        if not created:
            reminder.reminder_date = reminder_date
            reminder.reminder_time = reminder_time
            reminder.message = message
            reminder.save()
        
        messages.success(request, f'Reminder set for {ipo.company_name}!')
        return redirect('ipo_app:ipo_detail', pk=ipo_id)
    
    return render(request, 'ipo_app/set_reminder.html', {'ipo': ipo})

@login_required
def apply_ipo(request, ipo_id):
    ipo = get_object_or_404(IPO, pk=ipo_id)
    if request.method == 'POST':
        quantity = request.POST.get('quantity', 0)
        remarks = request.POST.get('remarks', '')
        
        # Check if user already applied
        existing_application = IPOApplication.objects.filter(user=request.user, ipo=ipo).first()
        if existing_application:
            messages.warning(request, f'You have already applied for {ipo.company_name}. You can update your application.')
            return redirect('ipo_app:my_applications')
        
        # Create new application
        application = IPOApplication.objects.create(
            user=request.user,
            ipo=ipo,
            quantity_applied=quantity,
            remarks=remarks,
            status='applied'
        )
        
        # Send notification to admin
        IPONotification.objects.create(
            user=User.objects.filter(is_staff=True).first(),
            message=f'New application received for {ipo.company_name} from {request.user.username}'
        )
        
        messages.success(request, f'Application submitted successfully for {ipo.company_name}! Your application is under review.')
        return redirect('ipo_app:my_applications')
    
    return render(request, 'ipo_app/apply_ipo.html', {'ipo': ipo})

@login_required
@user_passes_test(is_admin)
def manage_applications(request):
    applications = IPOApplication.objects.all().order_by('-application_date')
    pending_count = applications.filter(status='applied').count()
    approved_count = applications.filter(status='approved').count()
    rejected_count = applications.filter(status='rejected').count()
    
    context = {
        'applications': applications,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    }
    return render(request, 'ipo_app/manage_applications.html', context)

@login_required
@user_passes_test(is_admin)
def update_application_status(request, application_id):
    application = get_object_or_404(IPOApplication, pk=application_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        remarks = request.POST.get('admin_remarks', '')
        
        application.status = new_status
        application.remarks = remarks
        application.save()
        
        # Send notification to user
        status_message = f'Your application for {application.ipo.company_name} has been {new_status}.'
        if remarks:
            status_message += f' Remarks: {remarks}'
        
        IPONotification.objects.create(
            user=application.user,
            message=status_message
        )
        
        messages.success(request, f'Application status updated to {new_status}.')
        return redirect('ipo_app:manage_applications')
    
    return render(request, 'ipo_app/update_application_status.html', {'application': application})

@login_required
def my_reminders(request):
    reminders = IPOReminder.objects.filter(user=request.user, is_active=True).order_by('reminder_date')
    return render(request, 'ipo_app/my_reminders.html', {'reminders': reminders})

@login_required
def my_applications(request):
    applications = IPOApplication.objects.filter(user=request.user).order_by('-application_date')
    return render(request, 'ipo_app/my_applications.html', {'applications': applications})

@login_required
def delete_reminder(request, reminder_id):
    reminder = get_object_or_404(IPOReminder, pk=reminder_id, user=request.user)
    reminder.is_active = False
    reminder.save()
    messages.success(request, 'Reminder deleted successfully!')
    return redirect('ipo_app:my_reminders')

# Footer Pages
def privacy_policy(request):
    return render(request, 'ipo_app/privacy_policy.html')

def terms_of_service(request):
    return render(request, 'ipo_app/terms_of_service.html')

def cookie_policy(request):
    return render(request, 'ipo_app/cookie_policy.html')

def contact_us(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Save to database
        contact_message = ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        
        # Email content
        email_subject = f"Contact Form: {subject}"
        
        # HTML email template
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #1f2937; border-bottom: 2px solid #fbbf24; padding-bottom: 10px;">
                    New Contact Form Submission
                </h2>
                <div style="background: #f9fafb; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p><strong>Name:</strong> {name}</p>
                    <p><strong>Email:</strong> {email}</p>
                    <p><strong>Subject:</strong> {subject}</p>
                    <p><strong>Message:</strong></p>
                    <div style="background: white; padding: 15px; border-radius: 5px; border-left: 4px solid #fbbf24;">
                        {message}
                    </div>
                </div>
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                <p style="color: #6b7280; font-size: 12px;">
                    This message was sent from the Bluestock Fintech contact form at {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
                </p>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        plain_message = f"""
        New Contact Form Submission
        
        Name: {name}
        Email: {email}
        Subject: {subject}
        Message: {message}
        
        This message was sent from the Bluestock Fintech contact form.
        """
        
        try:
            # Send email to admin
            send_mail(
                subject=email_subject,
                message=strip_tags(plain_message),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],
                html_message=html_message,
                fail_silently=False,
            )
            
            # Send confirmation email to user
            confirmation_subject = "Thank you for contacting Bluestock Fintech"
            confirmation_html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #1f2937; border-bottom: 2px solid #fbbf24; padding-bottom: 10px;">
                        Thank you for contacting us!
                    </h2>
                    <p>Dear {name},</p>
                    <p>We have received your message and will get back to you within 24 hours.</p>
                    <div style="background: #f9fafb; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <p><strong>Your message:</strong></p>
                        <div style="background: white; padding: 15px; border-radius: 5px; border-left: 4px solid #fbbf24;">
                            {message}
                        </div>
                    </div>
                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                    <p>Best regards,<br><strong>Bluestock Fintech Team</strong></p>
                    <p style="color: #6b7280; font-size: 12px;">
                        If you have any urgent queries, please call us at +91 98765 43210
                    </p>
                </div>
            </body>
            </html>
            """
            
            send_mail(
                subject=confirmation_subject,
                message=strip_tags(confirmation_html),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=confirmation_html,
                fail_silently=False,
            )
            
            messages.success(request, 'Thank you for your message! We will get back to you soon. A confirmation email has been sent to your email address.')
            
        except Exception as e:
            messages.error(request, f'Sorry, there was an error sending your message. Please try again later. Error: {str(e)}')
        
        return redirect('ipo_app:contact_us')
    
    return render(request, 'ipo_app/contact_us.html')

def about_us(request):
    return render(request, 'ipo_app/about_us.html')

def faq(request):
    return render(request, 'ipo_app/faq.html')

def sme_ipos(request):
    sme_ipos = IPO.objects.filter(issue_type='SME IPO').order_by('-created_at')
    context = {
        'ipos': sme_ipos,
        'ipo_type': 'SME IPOs',
        'total_count': sme_ipos.count(),
    }
    return render(request, 'ipo_app/specialized_ipos.html', context)

def main_board_ipos(request):
    main_board_ipos = IPO.objects.filter(issue_type__in=['Book Built Issue', 'Fixed Price Issue']).order_by('-created_at')
    context = {
        'ipos': main_board_ipos,
        'ipo_type': 'Main Board IPOs',
        'total_count': main_board_ipos.count(),
    }
    return render(request, 'ipo_app/specialized_ipos.html', context)

@login_required
@user_passes_test(is_admin)
def export_data_page(request):
    # Get filter parameters for preview
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Build queryset with filters
    queryset = IPO.objects.all()
    
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    if date_from:
        queryset = queryset.filter(open_date__gte=date_from)
    
    if date_to:
        queryset = queryset.filter(open_date__lte=date_to)
    
    context = {
        'total_count': IPO.objects.count(),
        'filtered_count': queryset.count(),
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'ipo_app/export_data.html', context)
