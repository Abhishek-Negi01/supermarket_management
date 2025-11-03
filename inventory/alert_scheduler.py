import schedule
import time
from django.core.management import call_command
from threading import Thread

class AlertScheduler:
    def __init__(self):
        self.running = False
    
    def start_scheduler(self):
        """Start the alert scheduler in a separate thread"""
        if not self.running:
            self.running = True
            scheduler_thread = Thread(target=self._run_scheduler, daemon=True)
            scheduler_thread.start()
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        # Schedule alert checks every hour
        schedule.every().hour.do(self._check_alerts)
        
        # Schedule daily analytics update at midnight
        schedule.every().day.at("00:00").do(self._update_analytics)
        
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def _check_alerts(self):
        """Run alert check command"""
        try:
            call_command('check_alerts')
            print("Alert check completed successfully")
        except Exception as e:
            print(f"Alert check failed: {e}")
    
    def _update_analytics(self):
        """Update daily analytics"""
        try:
            from .analytics import InventoryAnalytics
            InventoryAnalytics.update_daily_analytics()
            print("Daily analytics updated successfully")
        except Exception as e:
            print(f"Analytics update failed: {e}")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.running = False

# Global scheduler instance
alert_scheduler = AlertScheduler()