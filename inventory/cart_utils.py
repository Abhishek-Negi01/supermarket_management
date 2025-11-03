def get_cart(session):
    return session.get('cart', {})

def add_to_cart(session, product_id, quantity=1):
    cart = get_cart(session)
    cart[str(product_id)] = cart.get(str(product_id), 0) + quantity
    session['cart'] = cart
    session.modified = True

def remove_from_cart(session, product_id):
    cart = get_cart(session)
    if str(product_id) in cart:
        del cart[str(product_id)]
        session['cart'] = cart
        session.modified = True

def clear_cart(session):
    session['cart'] = {}
    session.modified = True
