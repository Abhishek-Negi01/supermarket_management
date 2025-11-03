from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import InventoryAlert, SystemNotification
from .analytics import InventoryAnalytics

def staff_required(view_func):
    from django.contrib.auth.decorators import user_passes_test
    decorated_view_func = login_required(user_passes_test(lambda u: u.is_staff)(view_func))
    return decorated_view_func

@csrf_exempt
def mark_notification_read(request, notification_id):
    if request.method == 'POST':
        try:
            notification = SystemNotification.objects.get(id=notification_id)
            notification.is_read = True
            notification.save()
            return JsonResponse({'success': True})
        except SystemNotification.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Notification not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def dismiss_alert(request, alert_id):
    if request.method == 'POST':
        try:
            alert = InventoryAlert.objects.get(id=alert_id)
            alert.is_active = False
            alert.save()
            return JsonResponse({'success': True})
        except InventoryAlert.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Alert not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def trigger_alert_check(request):
    if request.method == 'POST':
        try:
            alerts_created = InventoryAnalytics.check_inventory_alerts()
            return JsonResponse({
                'success': True, 
                'alerts_created': alerts_created,
                'message': f'Created {alerts_created} new alerts'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@staff_required
def alert_management(request):
    """Alert management dashboard"""
    active_alerts = InventoryAlert.objects.filter(is_active=True).select_related('product')
    dismissed_alerts = InventoryAlert.objects.filter(is_active=False).select_related('product')[:20]
    
    context = {
        'active_alerts': active_alerts,
        'dismissed_alerts': dismissed_alerts,
        'alert_counts': {
            'low_stock': active_alerts.filter(alert_type='LOW_STOCK').count(),
            'out_of_stock': active_alerts.filter(alert_type='OUT_OF_STOCK').count(),
            'fast_moving': active_alerts.filter(alert_type='FAST_MOVING').count(),
        }
    }
    return render(request, 'inventory/alert_management.html', context)