from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'ipo', views.IPOViewSet)

app_name = 'ipo_app'

urlpatterns = [
    # Home URL - Redirects to login
    path('', views.home_view, name='home'),
    
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard URLs
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('analytics/', views.analytics_dashboard, name='analytics'),
    
    # Web URLs (Read-only for regular users)
    path('ipos/', views.IPOListView.as_view(), name='ipo_list'),
    path('ipo/<int:pk>/', views.IPODetailView.as_view(), name='ipo_detail'),
    
    # Admin-only IPO Management URLs
    path('ipo/create/', views.ipo_create, name='ipo_create'),
    path('ipo/<int:pk>/update/', views.ipo_update, name='ipo_update'),
    path('ipo/<int:pk>/delete/', views.ipo_delete, name='ipo_delete'),
    
    # API URLs (Admin only)
    path('api/', include(router.urls)),
    path('track-ipo/<int:pk>/', views.track_ipo, name='track_ipo'),
    path('notification/read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('all-notifications/', views.all_notifications, name='all_notifications'),
    path('send-notification/', views.send_notification, name='send_notification'),
    path('bulk-import/', views.bulk_import_ipos, name='bulk_import'),
    path('export-csv/', views.export_ipos_csv, name='export_csv'),
    path('set-reminder/<int:ipo_id>/', views.set_reminder, name='set_reminder'),
    path('apply-ipo/<int:ipo_id>/', views.apply_ipo, name='apply_ipo'),
    path('my-reminders/', views.my_reminders, name='my_reminders'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('delete-reminder/<int:reminder_id>/', views.delete_reminder, name='delete_reminder'),
    path('track-performance/<int:pk>/', views.track_performance, name='track_performance'),
    path('manage-applications/', views.manage_applications, name='manage_applications'),
    path('update-application-status/<int:application_id>/', views.update_application_status, name='update_application_status'),
    
    # Export Data
    path('export-data/', views.export_data_page, name='export_data'),
    path('export-csv/', views.export_ipos_csv, name='export_csv'),

    # Footer Pages
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('cookie-policy/', views.cookie_policy, name='cookie_policy'),
    path('contact-us/', views.contact_us, name='contact_us'),
    path('about-us/', views.about_us, name='about_us'),
    path('faq/', views.faq, name='faq'),
    path('sme-ipos/', views.sme_ipos, name='sme_ipos'),
    path('main-board-ipos/', views.main_board_ipos, name='main_board_ipos'),
] 