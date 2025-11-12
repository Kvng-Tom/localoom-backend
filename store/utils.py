
from .models import Cart

def merge_guest_cart(request):
    """
    Merge guest session cart into the authenticated user's cart after login.
    """
    if not request.user.is_authenticated:
        return

    session_key = request.session.session_key
    if not session_key:
        return

    guest_items = Cart.objects.filter(session_key=session_key, user__isnull=True)

    for item in guest_items:
        existing = Cart.objects.filter(user=request.user, product=item.product).first()
        if existing:
            existing.quantity += item.quantity
            existing.save()
            item.delete()
        else:
            item.user = request.user
            item.session_key = None
            item.save()
