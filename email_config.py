# Email Configuration for Bluestock Fintech
# Replace these values with your actual email credentials

# Gmail Configuration (Recommended)
EMAIL_CONFIG = {
    'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
    'EMAIL_HOST': 'smtp.gmail.com',
    'EMAIL_PORT': 587,
    'EMAIL_USE_TLS': True,
    'EMAIL_HOST_USER': 'your-email@gmail.com',  # Replace with your Gmail
    'EMAIL_HOST_PASSWORD': 'your-app-password',  # Replace with your app password
    'DEFAULT_FROM_EMAIL': 'Bluestock Fintech <your-email@gmail.com>',
    'CONTACT_EMAIL': 'support@bluestockfintech.com',  # Where contact form emails will be sent
}

# Alternative: Outlook/Hotmail Configuration
# EMAIL_CONFIG = {
#     'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
#     'EMAIL_HOST': 'smtp-mail.outlook.com',
#     'EMAIL_PORT': 587,
#     'EMAIL_USE_TLS': True,
#     'EMAIL_HOST_USER': 'your-email@outlook.com',
#     'EMAIL_HOST_PASSWORD': 'your-password',
#     'DEFAULT_FROM_EMAIL': 'Bluestock Fintech <your-email@outlook.com>',
#     'CONTACT_EMAIL': 'support@bluestockfintech.com',
# }

# Alternative: Yahoo Configuration
# EMAIL_CONFIG = {
#     'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
#     'EMAIL_HOST': 'smtp.mail.yahoo.com',
#     'EMAIL_PORT': 587,
#     'EMAIL_USE_TLS': True,
#     'EMAIL_HOST_USER': 'your-email@yahoo.com',
#     'EMAIL_HOST_PASSWORD': 'your-app-password',
#     'DEFAULT_FROM_EMAIL': 'Bluestock Fintech <your-email@yahoo.com>',
#     'CONTACT_EMAIL': 'support@bluestockfintech.com',
# }

# Instructions:
# 1. Choose your email provider above
# 2. Replace 'your-email@gmail.com' with your actual email
# 3. Replace 'your-app-password' with your email password or app password
# 4. For Gmail, you need to:
#    - Enable 2-factor authentication
#    - Generate an app password
#    - Use the app password instead of your regular password
# 5. Copy the EMAIL_CONFIG values to your settings.py file 