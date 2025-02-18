from django.shortcuts import redirect
from django.urls import reverse

def login_required_custom(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?next={request.path}")
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func