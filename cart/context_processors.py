from .models import Cart


def cart_context(request):
    """
    Makes cart available in all templates.
    Shows cart icon with item count in header.
    """
    cart = None
    if request.session.session_key:
        try:
            cart = Cart.objects.get(session_key=request.session.session_key)
        except Cart.DoesNotExist:
            pass

    return {
        'cart': cart,
        'cart_total_items': cart.total_items if cart else 0
    }
