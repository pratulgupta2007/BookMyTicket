from django.contrib.auth import logout
from django.shortcuts import redirect
from functools import wraps

def on_group_check(user):
    if user.groups is None:
        return True
    elif user.groups.filter(name='Theater Admin').exists():
        return False
    else: return True

def user_passes_test_with_logout():
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user=request.user
            if user.is_authenticated:
                if not on_group_check(request.user):
                    logout(request)
                    return redirect('account_login')
            else:
                return redirect('account_login')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator