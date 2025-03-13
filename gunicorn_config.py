# Gunicorn configuration
bind = "127.0.0.1:5000"
workers = 2
threads = 2
accesslog = "-"
errorlog = "-"
capture_output = True
enable_stdio_inheritance = True
forwarded_allow_ips = '*'  # Trust X-Forwarded-* headers
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
} 