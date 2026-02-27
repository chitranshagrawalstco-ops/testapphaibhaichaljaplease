from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import MenuItem, Category, Setting, PageView, Order, OrderItem
from app.extensions import db
from datetime import date

public_bp = Blueprint('public', __name__)

@public_bp.before_request
def track_views():
    if request.endpoint == 'public.index':
        today = date.today()
        view = PageView.query.filter_by(date=today).first()
        if view:
            view.count += 1
        else:
            view = PageView(date=today, count=1)
            db.session.add(view)
        db.session.commit()

@public_bp.route('/')
def index():
    settings = {s.key: s.value for s in Setting.query.all()}
    return render_template('public/index.html', settings=settings)

@public_bp.route('/menu')
def menu():
    categories = Category.query.all()
    # If a category is selected via query param
    cat_id = request.args.get('category', type=int)
    if cat_id:
        items = MenuItem.query.filter_by(category_id=cat_id, is_available=True).all()
    else:
        items = MenuItem.query.filter_by(is_available=True).all()
        
    settings = {s.key: s.value for s in Setting.query.all()}
    return render_template('public/menu.html', items=items, categories=categories, settings=settings)

@public_bp.route('/create-order', methods=['POST'])
def create_order():
    data = request.json
    if not data or 'items' not in data:
        return {"error": "Invalid data"}, 400

    settings = {s.key: s.value for s in Setting.query.all()}
    if settings.get('shop_status') != 'open':
        return {"error": "Shop is closed. Please check back next time."}, 403
        
    try:
        new_order = Order(
            customer_name=data.get('name'),
            customer_phone=data.get('phone'),
            order_type=data.get('order_type'),
            estimated_arrival_time=data.get('arrival_time'),
            total_price=data.get('total_price'),
            status='Pending'
        )
        db.session.add(new_order)
        db.session.flush() # Get order ID
        
        for item in data['items']:
            order_item = OrderItem(
                order_id=new_order.id,
                menu_item_id=item['id'],
                quantity=item['quantity'],
                price_at_time=item['price']
            )
            db.session.add(order_item)
            
        db.session.commit()
        return {"success": True, "order_id": new_order.id}, 201
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

@public_bp.route('/order-choice')
def order_choice():
    settings = {s.key: s.value for s in Setting.query.all()}
    if settings.get('shop_status') != 'open':
        flash('Shop is closed. Please check back next time.', 'error')
        return redirect(url_for('public.menu'))
    return render_template('public/order_choice.html', settings=settings)

@public_bp.route('/order-success/<int:order_id>')
def order_success(order_id):
    order = Order.query.get_or_404(order_id)
    settings = {s.key: s.value for s in Setting.query.all()}
    phone = settings.get('phone', '').replace(' ', '').replace('+', '')
    return render_template('public/order_success.html', order=order, phone=phone)
