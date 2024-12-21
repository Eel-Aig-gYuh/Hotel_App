from datetime import datetime


def cart_stats(cart):
    total_quantity, total_amount = 0, 0
    if cart:
        for c in cart.values():
            total_quantity += c['quantity']
            total_amount += int(c['quantity']) * int(c['room_type_price_per_night'])

    return {
        "total_quantity": total_quantity,
        "total_amount": total_amount
    }

def format_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d').date()