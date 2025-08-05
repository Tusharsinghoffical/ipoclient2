from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class IPO(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('listed', 'Listed'),
    ]
    
    company_name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    price_band = models.CharField(max_length=100)
    open_date = models.DateField()
    close_date = models.DateField()
    issue_size = models.CharField(max_length=100)
    issue_type = models.CharField(max_length=100)
    listing_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    ipo_price = models.FloatField(null=True, blank=True)
    listing_price = models.FloatField(null=True, blank=True)
    current_market_price = models.FloatField(null=True, blank=True)
    rhp_pdf = models.FileField(upload_to='docs/', null=True, blank=True)
    drhp_pdf = models.FileField(upload_to='docs/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def listing_gain(self):
        if self.ipo_price and self.listing_price:
            return round(((self.listing_price - self.ipo_price) / self.ipo_price) * 100, 2)
        return None
    
    @property
    def current_return(self):
        if self.ipo_price and self.current_market_price:
            return round(((self.current_market_price - self.ipo_price) / self.ipo_price) * 100, 2)
        return None
    
    def __str__(self):
        return self.company_name
    
    class Meta:
        ordering = ['-open_date']

# User IPO Watchlist
class IPOTracking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ipo = models.ForeignKey(IPO, on_delete=models.CASCADE)
    tracked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'ipo')

# IPO Notification
class IPONotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return self.message

class IPOReminder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ipo = models.ForeignKey(IPO, on_delete=models.CASCADE)
    reminder_date = models.DateField()
    reminder_time = models.TimeField()
    message = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'ipo']
    
    def __str__(self):
        return f"{self.user.username} - {self.ipo.company_name}"

class IPOApplication(models.Model):
    APPLICATION_STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('allotted', 'Allotted'),
        ('not_allotted', 'Not Allotted'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ipo = models.ForeignKey(IPO, on_delete=models.CASCADE)
    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS_CHOICES, default='applied')
    quantity_applied = models.IntegerField(default=0)
    remarks = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['user', 'ipo']
    
    def __str__(self):
        return f"{self.user.username} - {self.ipo.company_name} ({self.get_status_display()})"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"
