from django.contrib import admin
from .models import IPO, IPOTracking, IPONotification, IPOReminder, IPOApplication, ContactMessage

@admin.register(IPO)
class IPOAdmin(admin.ModelAdmin):
    list_display = [
        'company_name', 'status', 'open_date', 'close_date', 
        'listing_date', 'ipo_price', 'listing_price', 'current_market_price'
    ]
    list_filter = ['status', 'open_date', 'close_date', 'listing_date']
    search_fields = ['company_name']
    readonly_fields = ['listing_gain', 'current_return', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('company_name', 'logo', 'status')
        }),
        ('IPO Details', {
            'fields': ('price_band', 'open_date', 'close_date', 'issue_size', 'issue_type')
        }),
        ('Pricing Information', {
            'fields': ('ipo_price', 'listing_price', 'current_market_price')
        }),
        ('Calculated Fields', {
            'fields': ('listing_gain', 'current_return'),
            'classes': ('collapse',)
        }),
        ('Documents', {
            'fields': ('rhp_pdf', 'drhp_pdf')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            readonly = list(self.readonly_fields)
            readonly.extend(['listing_gain', 'current_return'])
            return readonly
        return self.readonly_fields

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at']
    list_editable = ['is_read']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected messages as read"
    
    actions = ['mark_as_read']
