from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def get_user_role(user):
    """Get user role from Employee model"""
    if user.is_superuser:
        return 'ADMIN'
    try:
        return user.employee.role
    except:
        return None

def role_required(*allowed_roles):
    """Decorator to restrict access based on user role"""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            user_role = get_user_role(request.user)
            
            if user_role in allowed_roles or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('home')
        return wrapper
    return decorator

# Specific role decorators
def admin_required(view_func):
    return role_required('ADMIN')(view_func)

def manager_required(view_func):
    return role_required('ADMIN', 'MANAGER')(view_func)

def cashier_required(view_func):
    return role_required('ADMIN', 'MANAGER', 'CASHIER')(view_func)

def stock_keeper_required(view_func):
    return role_required('ADMIN', 'MANAGER', 'STOCK')(view_func)
