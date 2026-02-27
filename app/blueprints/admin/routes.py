from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required
from app.models import MenuItem, Category, Setting, PageView, Order, OrderItem, User
import bcrypt
from app.extensions import db
from app.services.image_service import save_image, delete_image
from datetime import date, timedelta, datetime
from sqlalchemy import func, text

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
def dashboard():
    total_items = MenuItem.query.count()
    total_categories = Category.query.count()
    total_orders = Order.query.filter_by(is_deleted=False).count()
    
    today = date.today()
    
    # Advanced Stats
    # Today's Sales (Completed only)
    today_sales = db.session.query(func.sum(Order.total_price)).filter(
        func.date(Order.created_at) == today,
        Order.status.in_(['Pending', 'Completed']),
        Order.is_deleted == False
    ).scalar() or 0
    
    # Last 30 Days Sales
    thirty_days_ago = today - timedelta(days=30)
    thirty_day_sales = db.session.query(func.sum(Order.total_price)).filter(
        Order.created_at >= thirty_days_ago,
        Order.status.in_(['Pending', 'Completed']),
        Order.is_deleted == False
    ).scalar() or 0
    
    # 7 Day Sales Trend
    sales_trend = []
    max_sale = 0
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        s = db.session.query(func.sum(Order.total_price)).filter(
            func.date(Order.created_at) == day,
            Order.status.in_(['Pending', 'Completed']),
            Order.is_deleted == False
        ).scalar() or 0
        if s > max_sale: max_sale = s
        sales_trend.append({
            'label': day.strftime('%a'),
            'value': s
        })
    
    # Add percentage height for trend chart
    for day in sales_trend:
        # max_sale is already a number (scalar returns None or number)
        if max_sale and float(max_sale) > 0:
            day['height'] = int((float(day['value']) / float(max_sale) * 100))
        else:
            day['height'] = 0

    # Most Ordered Today
    most_ordered_today = db.session.query(
        MenuItem.name, 
        MenuItem.image_path,
        func.sum(OrderItem.quantity).label('qty')
    ).join(OrderItem).join(Order).filter(
        func.date(Order.created_at) == today,
        Order.status != 'Cancelled',
        Order.is_deleted == False
    ).group_by(MenuItem.id).order_by(text('qty DESC')).limit(5).all()

    today_views = PageView.query.filter_by(date=today).first()
    today_count = today_views.count if today_views else 0
    
    recent_orders = Order.query.filter_by(is_deleted=False).order_by(Order.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                           total_items=total_items, 
                           total_categories=total_categories,
                           total_orders=total_orders,
                           today_sales=today_sales,
                           thirty_day_sales=thirty_day_sales,
                           sales_trend=sales_trend,
                           most_ordered=most_ordered_today,
                           today_count=today_count,
                           recent_orders=recent_orders)

@admin_bp.route('/orders')
@login_required
def orders():
    all_orders = Order.query.filter_by(is_deleted=False).order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=all_orders)

@admin_bp.route('/orders/update-status/<int:id>')
@login_required
def update_order_status(id):
    order = Order.query.get_or_404(id)
    new_status = request.args.get('status')
    if new_status in ['Pending', 'Completed', 'Cancelled']:
        order.status = new_status
        db.session.commit()
        flash(f'Order #{id} status updated to {new_status}.', 'success')
    return redirect(url_for('admin.orders'))

@admin_bp.route('/orders/delete/<int:id>')
@login_required
def delete_order(id):
    order = Order.query.get_or_404(id)
    order.is_deleted = True
    db.session.commit()
    flash(f'Order #{id} has been deleted.', 'success')
    return redirect(url_for('admin.orders'))

# Categories CRUD
@admin_bp.route('/categories')
@login_required
def categories():
    all_categories = Category.query.all()
    return render_template('admin/categories.html', categories=all_categories)

@admin_bp.route('/categories/add', methods=['POST'])
@login_required
def add_category():
    name = request.form.get('name')
    if name:
        new_cat = Category(name=name)
        db.session.add(new_cat)
        db.session.commit()
        flash('Category added!', 'success')
    return redirect(url_for('admin.categories'))

@admin_bp.route('/categories/delete/<int:id>')
@login_required
def delete_category(id):
    cat = Category.query.get_or_404(id)
    db.session.delete(cat)
    db.session.commit()
    flash('Category deleted!', 'success')
    return redirect(url_for('admin.categories'))

# Menu Items CRUD
@admin_bp.route('/items')
@login_required
def items():
    all_items = MenuItem.query.all()
    all_categories = Category.query.all()
    return render_template('admin/items.html', items=all_items, categories=all_categories)

@admin_bp.route('/items/add', methods=['POST'])
@login_required
def add_item():
    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    category_id = request.form.get('category_id')
    is_non_veg = 'is_non_veg' in request.form
    image = request.files.get('image')
    
    image_path = save_image(image)
    
    new_item = MenuItem(
        name=name,
        description=description,
        price=float(price),
        category_id=category_id,
        is_non_veg=is_non_veg,
        image_path=image_path
    )
    db.session.add(new_item)
    db.session.commit()
    flash('Item added!', 'success')
    return redirect(url_for('admin.items'))

@admin_bp.route('/items/edit/<int:id>', methods=['POST'])
@login_required
def edit_item(id):
    item = MenuItem.query.get_or_404(id)
    item.name = request.form.get('name')
    item.description = request.form.get('description')
    item.price = float(request.form.get('price'))
    item.category_id = request.form.get('category_id')
    item.is_non_veg = 'is_non_veg' in request.form
    item.is_available = 'is_available' in request.form
    
    image = request.files.get('image')
    if image:
        delete_image(item.image_path)
        item.image_path = save_image(image)
        
    db.session.commit()
    flash('Item updated!', 'success')
    return redirect(url_for('admin.items'))

@admin_bp.route('/items/delete/<int:id>')
@login_required
def delete_item(id):
    item = MenuItem.query.get_or_404(id)
    delete_image(item.image_path)
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted!', 'success')
    return redirect(url_for('admin.items'))

# Settings
@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    from flask_login import current_user
    if request.method == 'POST':
        # Check if this is an account update
        if 'update_account' in request.form:
            new_username = request.form.get('username')
            new_password = request.form.get('password')
            
            if new_username:
                # Check if username is already taken by another user
                existing_user = User.query.filter(User.username == new_username, User.id != current_user.id).first()
                if existing_user:
                    flash('Username already exists!', 'error')
                    return redirect(url_for('admin.settings'))
                current_user.username = new_username
            
            if new_password:
                hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                current_user.password_hash = hashed_pw
            
            db.session.commit()
            flash('Account credentials updated!', 'success')
            return redirect(url_for('admin.settings'))

        # Standard settings update
        keys = ['phone', 'whatsapp_msg', 'upi_id', 'address', 'hours_weekday', 'hours_saturday', 'hours_sunday', 'banner_url']
        for key in keys:
            if key in request.form:
                s = Setting.query.filter_by(key=key).first()
                if s: s.value = request.form.get(key)
        
        # Handle the shop_status checkbox specifically
        shop_status = Setting.query.filter_by(key='shop_status').first()
        status_val = 'open' if 'shop_status' in request.form else 'closed'
        if shop_status:
            shop_status.value = status_val
        else:
            db.session.add(Setting(key='shop_status', value=status_val))
            
        db.session.commit()
        flash('Settings updated!', 'success')
        return redirect(url_for('admin.settings'))
        
    all_settings = {s.key: s.value for s in Setting.query.all()}
    return render_template('admin/settings.html', settings=all_settings)
