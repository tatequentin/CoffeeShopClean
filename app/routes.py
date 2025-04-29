from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import os
import random
from werkzeug.utils import secure_filename

bp = Blueprint('main', __name__)

menu_items = [
    {'name': 'Honey Lavender Espresso', 'description': 'Doppio espresso, honey, lavender syrup.', 'price': 4.79, 'image': 'Honey-Lavender-Espresso.png'},
    {'name': 'Bronze Banana Blast', 'description': 'Banana cordial, caramel syrup, doppio espresso shot, milk, blended with ice and topped with whipped cream and caramelized bananas.', 'price': 9.99, 'image': 'Bronze-Banana-Blast.png'},
    {'name': 'Salted Caramel Mocha', 'description': 'Doppio espresso shot, salted caramel syrup, non-alcoholic chocolate bitters, milk, topped with shaved dark chocolate.', 'price': 7.99, 'image': 'Salted-Caramel-Mocha.png'},
    {'name': 'Very Berry Hibiscus Cooler', 'description': 'Blackberries, blueberries, mint, and agave muddled in a shaker tin, shaken and strained over ice, topped with sparkling water and mint garnish.', 'price': 8.50, 'image': 'Very-Berry-Hibiscus-Cooler.png'},
    {'name': 'Pistachio Cardamom Roll', 'description': 'Cardamom and pistachio baked into a house-made brioche roll, topped with shaved pistachios.', 'price': 6.50, 'image': 'Pistachio-Cardamom-Roll.jpg'},
    {'name': 'Truly Blue Tiramisu', 'description': 'House-made tiramisu base with fresh espresso and blueberry syrup baked in, then topped with blueberry compote and an Oreo crust.', 'price': 12.99, 'image': 'Truly-Blue-Tiramisu.png'}
]

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/menu')
def menu():
    query = request.args.get('q', '').lower()
    if query:
        filtered_items = [item for item in menu_items if query in item['name'].lower() or query in item['description'].lower()]
    else:
        filtered_items = menu_items
    return render_template('menu.html', items=filtered_items, query=query)

@bp.route('/add-to-cart/<int:item_id>')
def add_to_cart(item_id):
    item = menu_items[item_id]
    cart = session.get('cart', [])

    cart.append({
        'name': item['name'],
        'description': item['description'],
        'price': item['price'],
        'image': item['image']
    })

    session['cart'] = cart
    flash(f"{item['name']} added to cart!")
    return redirect(url_for('main.menu'))

@bp.route('/cart')
def cart():
    cart_items = session.get('cart', [])

    subtotal = sum(item['price'] for item in cart_items)
    tax = subtotal * 0.07
    grand_total = subtotal + tax

    suggestions = []
    if menu_items:
        sampled_items = random.sample(menu_items, k=min(2, len(menu_items)))
        for idx, item in enumerate(sampled_items):
            suggestions.append({
                'index': menu_items.index(item),
                'name': item['name'],
                'price': item['price'],
                'description': item['description'],
                'image': item['image']
            })

    return render_template('cart.html', cart_items=cart_items, subtotal=subtotal, tax=tax, grand_total=grand_total, suggestions=suggestions)

@bp.route('/add-item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        image_file = request.files['image']

        filename = secure_filename(image_file.filename)
        image_path = os.path.join('app/static/img', filename)
        image_file.save(image_path)

        menu_items.append({
            'name': name,
            'description': description,
            'price': price,
            'image': filename
        })

        flash('Menu item added!')
        return redirect(url_for('main.menu'))

    return render_template('add_item.html')

@bp.route('/remove-from-cart/<int:item_index>')
def remove_from_cart(item_index):
    cart = session.get('cart', [])
    if 0 <= item_index < len(cart):
        removed_item = cart.pop(item_index)
        flash(f"Removed {removed_item['name']} from cart.")
        session['cart'] = cart
    else:
        flash("Item not found in cart.")
    return redirect(url_for('main.cart'))

@bp.route('/confirm-order')
def confirm_order():
    session['cart'] = []
    return render_template('order_confirmed.html')

@bp.route('/order-confirmed')
def order_confirmed():
    return render_template('order_confirmed.html')

@bp.route('/clear-cart')
def clear_cart():
    session['cart'] = []
    flash('Cart cleared.')
    return redirect(url_for('main.menu'))
