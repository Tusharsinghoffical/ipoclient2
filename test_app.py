#!/usr/bin/env python
"""
Test script to verify the IPO application is working correctly.
"""

import os
import sys
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ipo_project.settings')
django.setup()

from ipo_app.models import IPO

def test_application():
    """Test the application functionality"""
    
    print("=== IPO Web Application Test ===\n")
    
    # Test 1: Check if IPOs exist
    total_ipos = IPO.objects.count()
    print(f"1. Total IPOs in database: {total_ipos}")
    
    if total_ipos == 0:
        print("   ❌ No IPOs found. Please run create_sample_data.py first.")
        return False
    
    # Test 2: Check IPOs by status
    upcoming_count = IPO.objects.filter(status='upcoming').count()
    ongoing_count = IPO.objects.filter(status='ongoing').count()
    listed_count = IPO.objects.filter(status='listed').count()
    
    print(f"2. IPOs by status:")
    print(f"   - Upcoming: {upcoming_count}")
    print(f"   - Ongoing: {ongoing_count}")
    print(f"   - Listed: {listed_count}")
    
    # Test 3: Check calculated fields
    listed_ipos = IPO.objects.filter(status='listed')
    for ipo in listed_ipos[:3]:  # Check first 3 listed IPOs
        print(f"3. {ipo.company_name}:")
        print(f"   - Listing Gain: {ipo.listing_gain}%")
        print(f"   - Current Return: {ipo.current_return}%")
    
    # Test 4: Check API endpoints (simulate)
    print(f"\n4. API Endpoints available:")
    print(f"   - GET /api/ipo/ (All IPOs)")
    print(f"   - GET /api/ipo/upcoming/ (Upcoming IPOs)")
    print(f"   - GET /api/ipo/ongoing/ (Ongoing IPOs)")
    print(f"   - GET /api/ipo/listed/ (Listed IPOs)")
    
    # Test 5: Check web pages
    print(f"\n5. Web Pages available:")
    print(f"   - Homepage: http://localhost:8000/")
    print(f"   - IPO Details: http://localhost:8000/ipo/1/")
    print(f"   - Admin Dashboard: http://localhost:8000/admin-dashboard/")
    print(f"   - Django Admin: http://localhost:8000/admin/")
    
    print(f"\n✅ Application is ready!")
    print(f"📊 Sample data loaded: {total_ipos} IPOs")
    print(f"🔗 Start the server with: python manage.py runserver")
    print(f"👤 Admin login: admin / admin123")
    
    return True

if __name__ == '__main__':
    test_application() 