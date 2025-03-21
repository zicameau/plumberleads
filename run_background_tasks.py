#!/usr/bin/env python
"""
Background task runner for PlumberLeads application.
This script runs periodic tasks like releasing expired lead reservations.
"""

import time
from app.tasks.lead_tasks import release_expired_reservations

def run_background_tasks():
    """Run background tasks periodically"""
    print("Starting background tasks...")
    
    while True:
        try:
            # Release expired reservations
            release_expired_reservations()
            
            # Wait for 5 minutes before next check
            time.sleep(300)
            
        except Exception as e:
            print(f"Error in background task: {e}")
            # Wait for 1 minute before retrying
            time.sleep(60)

if __name__ == '__main__':
    run_background_tasks() 