from django.http import HttpResponseForbidden

def vendor_or_admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Login required.")
        customer = request.user.customer
        if customer.role in ['VENDOR', 'ADMIN']:
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("You are not allowed to perform this action.")
    return wrapper
