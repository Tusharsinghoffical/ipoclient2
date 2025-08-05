#!/usr/bin/env python
"""
Script to create sample IPO data for testing the application.
Run this script after setting up the Django project.
"""

import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ipo_project.settings')
django.setup()

from ipo_app.models import IPO

def create_sample_ipos():
    """Create sample IPO data"""
    
    # Sample IPOs data
    sample_ipos = [
        {
            'company_name': 'TechCorp Solutions Ltd',
            'price_band': '₹450 - ₹500',
            'open_date': date.today() + timedelta(days=15),
            'close_date': date.today() + timedelta(days=18),
            'issue_size': '₹1,200 Crores',
            'issue_type': 'Book Built Issue',
            'status': 'upcoming',
            'ipo_price': None,
            'listing_price': None,
            'current_market_price': None,
        },
        {
            'company_name': 'Green Energy Ltd',
            'price_band': '₹200 - ₹220',
            'open_date': date.today() - timedelta(days=2),
            'close_date': date.today() + timedelta(days=1),
            'issue_size': '₹800 Crores',
            'issue_type': 'Fixed Price Issue',
            'status': 'ongoing',
            'ipo_price': None,
            'listing_price': None,
            'current_market_price': None,
        },
        {
            'company_name': 'Digital Payments Ltd',
            'price_band': '₹150 - ₹180',
            'open_date': date.today() - timedelta(days=30),
            'close_date': date.today() - timedelta(days=27),
            'listing_date': date.today() - timedelta(days=20),
            'issue_size': '₹600 Crores',
            'issue_type': 'Book Built Issue',
            'status': 'listed',
            'ipo_price': 165.0,
            'listing_price': 185.0,
            'current_market_price': 210.0,
        },
        {
            'company_name': 'Healthcare Innovations Ltd',
            'price_band': '₹300 - ₹350',
            'open_date': date.today() - timedelta(days=45),
            'close_date': date.today() - timedelta(days=42),
            'listing_date': date.today() - timedelta(days=35),
            'issue_size': '₹900 Crores',
            'issue_type': 'Book Built Issue',
            'status': 'listed',
            'ipo_price': 325.0,
            'listing_price': 340.0,
            'current_market_price': 380.0,
        },
        {
            'company_name': 'E-commerce Solutions Ltd',
            'price_band': '₹400 - ₹450',
            'open_date': date.today() + timedelta(days=30),
            'close_date': date.today() + timedelta(days=33),
            'issue_size': '₹1,500 Crores',
            'issue_type': 'Book Built Issue',
            'status': 'upcoming',
            'ipo_price': None,
            'listing_price': None,
            'current_market_price': None,
        },
        {
            'company_name': 'Fintech Innovations Ltd',
            'price_band': '₹250 - ₹280',
            'open_date': date.today() - timedelta(days=60),
            'close_date': date.today() - timedelta(days=57),
            'listing_date': date.today() - timedelta(days=50),
            'issue_size': '₹750 Crores',
            'issue_type': 'Book Built Issue',
            'status': 'listed',
            'ipo_price': 265.0,
            'listing_price': 290.0,
            'current_market_price': 275.0,
        },
        {
            'company_name': 'AI Technology Ltd',
            'price_band': '₹500 - ₹550',
            'open_date': date.today() + timedelta(days=45),
            'close_date': date.today() + timedelta(days=48),
            'issue_size': '₹2,000 Crores',
            'issue_type': 'Book Built Issue',
            'status': 'upcoming',
            'ipo_price': None,
            'listing_price': None,
            'current_market_price': None,
        },
        {
            'company_name': 'Manufacturing Corp Ltd',
            'price_band': '₹180 - ₹200',
            'open_date': date.today() - timedelta(days=75),
            'close_date': date.today() - timedelta(days=72),
            'listing_date': date.today() - timedelta(days=65),
            'issue_size': '₹500 Crores',
            'issue_type': 'Fixed Price Issue',
            'status': 'listed',
            'ipo_price': 190.0,
            'listing_price': 175.0,
            'current_market_price': 160.0,
        },
    ]
    
    created_count = 0
    
    for ipo_data in sample_ipos:
        # Check if IPO already exists
        if not IPO.objects.filter(company_name=ipo_data['company_name']).exists():
            ipo = IPO.objects.create(**ipo_data)
            created_count += 1
            print(f"Created IPO: {ipo.company_name} - {ipo.get_status_display()}")
        else:
            print(f"IPO already exists: {ipo_data['company_name']}")
    
    print(f"\nTotal IPOs created: {created_count}")
    print(f"Total IPOs in database: {IPO.objects.count()}")
    
    # Print summary by status
    for status, count in IPO.objects.values_list('status').annotate(count=django.db.models.Count('id')):
        print(f"{status.title()} IPOs: {count}")

if __name__ == '__main__':
    print("Creating sample IPO data...")
    create_sample_ipos()
    print("\nSample data creation completed!") 