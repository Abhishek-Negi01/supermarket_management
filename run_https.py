#!/usr/bin/env python
import os
import sys
import ssl
from django.core.management import execute_from_command_line
from django.core.management.commands.runserver import Command as runserver

# Allow HTTP for camera access (development only)
runserver.default_port = "8000"

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'supermarket_management.settings')
    
    # Create self-signed certificate for HTTPS
    import subprocess
    try:
        # Generate certificate if it doesn't exist
        if not os.path.exists('server.crt'):
            subprocess.run([
                'openssl', 'req', '-x509', '-newkey', 'rsa:4096', 
                '-keyout', 'server.key', '-out', 'server.crt', 
                '-days', '365', '-nodes', '-subj', '/CN=localhost'
            ], check=True)
    except:
        print("OpenSSL not available. Use ngrok instead.")
        sys.exit(1)
    
    execute_from_command_line(sys.argv)