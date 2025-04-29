from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import json
import os
import random

bp = Blueprint('main', __name__)
DATA_DIR = os.path.join('app', 'data')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
MENU_FILE = os.path.join(DATA_DIR, 'menu.json')

def load_users():
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def load_menu():
    with open(MENU_FILE, 'r') as f:
        return json.load(f)

def save_menu(menu):
    with open(MENU_FILE, 'w') as f:
        json.dump(menu, f, indent=4)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_users()
        username = request.form['username']
        password = request.form['password']
        for user in users:
            if user['username'] == username and user['password'] == password:
                session['username'] = username
                session['is_admin'] = user.get('role') == 'admin'
                flash('Logged in successfully!')
                return redirect(url_for('main.index'))
        flash('Invalid credentials.')
    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out.')
    return redirect(url_for('main.index'))

@bp.route('/sales-report')
def sales_report():
    if not session.get('is_admin'):
        flash('Admin access required.')
        return redirect(url_for('main.index'))
    return render_template('sales_report.html')

@bp.route('/modify-items', methods=['GET', 'POST'])
def modify_items():
    if not session.get('is_admin'):
        flash('Admin access required.')
        return redirect(url_for('main.index'))

    menu = load_menu()

    if request.method == 'POST':
        index = int(request.form['item_index'])
        menu[index]['name'] = request.form['new_name']
        menu[index]['description'] = request.form['new_description']
        menu[index]['price'] = float(request.form['new_price'])

        save_menu(menu)
        flash('Item updated successfully!')
        return redirect(url_for('main.modify_items'))

    return render_template('modify_items.html', menu=menu)

@bp.route('/promote-user', methods=['GET', 'POST'])
def promote_user():
    if not session.get('is_admin'):
        flash('Admin access required.')
        return redirect(url_for('main.index'))
    users = load_users()
    if request.method == 'POST':
        index = int(request.form['user_index'])
        users[index]['role'] = 'admin'
        save_users(users)
        flash('User promoted!')
        return redirect(url_for('main.promote_user'))
    return render_template('promote_user.html', users=users)

@bp.route('/menu')
def menu():
    menu_items = load_menu()
    query = request.args.get('q', '').lower()
    if query:
        filtered = [item for item in menu_items if query in item['name'].lower() or query in item['description'].lower()]
    else:
        filtered = menu_items
    return render_template('menu.html', items=filtered, query=query)

@bp.route('/add-to-cart/<int:item_id>')
def add_to_cart(item_id):
    menu_items = load_menu()
    if 0 <= item_id < len(menu_items):
        item = menu_items[item_id]
        cart = session.get('cart', [])
        cart.append(item)
        session['cart'] = cart
        flash(f"{item['name']} added to cart!")
    else:
        flash("Item not found.")
    return redirect(url_for('main.menu'))

@bp.route('/cart')
def cart():
    cart_items = session.get('cart', [])

    subtotal = sum(item['price'] for item in cart_items)
    tax = subtotal * 0.07
    grand_total = subtotal + tax

    all_items = load_menu()
    suggestions = []
    if all_items:
        sampled_items = random.sample(all_items, k=min(2, len(all_items)))
        for item in sampled_items:
            suggestions.append({
                'index': all_items.index(item),
                'name': item['name'],
                'price': item['price'],
                'description': item['description'],
                'image': item['image']
            })

    return render_template('cart.html', cart_items=cart_items, subtotal=subtotal, tax=tax, grand_total=grand_total, suggestions=suggestions)

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

@bp.route('/add-item', methods=['GET', 'POST'])
def add_item():
    if not session.get('is_admin'):
        flash('Admin access required.')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        image_file = request.files['image']

        filename = secure_filename(image_file.filename)
        image_path = os.path.join('app/static/img', filename)
        image_file.save(image_path)

        menu = load_menu()
        menu.append({
            'name': name,
            'description': description,
            'price': price,
            'image': filename
        })
        save_menu(menu)

        flash('Menu item added!')
        return redirect(url_for('main.menu'))

    return render_template('add_item.html')

