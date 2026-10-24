from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from auth import admin_required, get_db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    conn = get_db()
    
    total_sales = conn.execute("SELECT SUM(total_amount) as total FROM orders WHERE payment_status = 'PAID'").fetchone()['total'] or 0
    total_orders = conn.execute("SELECT COUNT(id) as count FROM orders").fetchone()['count']
    total_customers = conn.execute("SELECT COUNT(id) as count FROM users WHERE role = 'customer'").fetchone()['count']
    total_products = conn.execute("SELECT COUNT(id) as count FROM products").fetchone()['count']
    pending_orders = conn.execute("SELECT COUNT(id) as count FROM orders WHERE order_status = 'Pending'").fetchone()['count']
    low_stock = conn.execute("SELECT COUNT(id) as count FROM products WHERE stock < 10").fetchone()['count']
    
    recent_orders = conn.execute("SELECT id, payment_status, order_status FROM orders ORDER BY created_at DESC LIMIT 5").fetchall()
    
    conn.close()
    
    stats = {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'total_products': total_products,
        'pending_orders': pending_orders,
        'low_stock': low_stock
    }
    
    return render_template('admin_dashboard.html', stats=stats, recent_orders=recent_orders)

@admin_bp.route('/products')
@admin_required
def products():
    conn = get_db()
    products = conn.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('admin_products.html', products=products)

@admin_bp.route('/products/add', methods=['GET', 'POST'])
@admin_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        brand = request.form.get('brand')
        category = request.form.get('category')
        price = request.form.get('price')
        stock = request.form.get('stock')
        description = request.form.get('description')
        image = request.form.get('image')
        badge = request.form.get('badge')
        
        conn = get_db()
        placeholder = '%s' if hasattr(conn, 'conn') else '?'
        conn.execute(f'''
            INSERT INTO products (name, brand, category, price, stock, description, image, badge)
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        ''', (name, brand, category, price, stock, description, image, badge))
        conn.commit()
        conn.close()
        
        flash('Product added successfully', 'success')
        return redirect(url_for('admin.products'))
        
    return render_template('admin_add_product.html')

@admin_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    conn = get_db()
    placeholder = '%s' if hasattr(conn, 'conn') else '?'
    
    if request.method == 'POST':
        name = request.form.get('name')
        brand = request.form.get('brand')
        category = request.form.get('category')
        price = request.form.get('price')
        stock = request.form.get('stock')
        description = request.form.get('description')
        image = request.form.get('image')
        badge = request.form.get('badge')
        
        conn.execute(f'''
            UPDATE products 
            SET name = {placeholder}, brand = {placeholder}, category = {placeholder},
                price = {placeholder}, stock = {placeholder}, description = {placeholder},
                image = {placeholder}, badge = {placeholder}
            WHERE id = {placeholder}
        ''', (name, brand, category, price, stock, description, image, badge, product_id))
        conn.commit()
        conn.close()
        
        flash(f'Product #{product_id} updated successfully!', 'success')
        return redirect(url_for('admin.products'))
        
    product = conn.execute(f"SELECT * FROM products WHERE id = {placeholder}", (product_id,)).fetchone()
    conn.close()
    
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('admin.products'))
        
    return render_template('admin_edit_product.html', product=product)

@admin_bp.route('/products/<int:product_id>/delete', methods=['POST'])
@admin_required
def delete_product(product_id):
    conn = get_db()
    placeholder = '%s' if hasattr(conn, 'conn') else '?'
    try:
        # Delete related order items if any
        conn.execute(f"DELETE FROM order_items WHERE product_id = {placeholder}", (product_id,))
        conn.execute(f"DELETE FROM products WHERE id = {placeholder}", (product_id,))
        conn.commit()
        flash(f'Product #{product_id} deleted successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting product: {e}', 'danger')
    finally:
        conn.close()
        
    return redirect(url_for('admin.products'))

@admin_bp.route('/inventory')
@admin_required
def inventory():
    conn = get_db()
    products = conn.execute("SELECT id, name, stock FROM products ORDER BY stock ASC").fetchall()
    conn.close()
    return render_template('admin_inventory.html', products=products)

@admin_bp.route('/orders')
@admin_required
def orders():
    conn = get_db()
    orders = conn.execute("SELECT * FROM orders ORDER BY created_at DESC").fetchall()
    conn.close()
    return render_template('admin_orders.html', orders=orders)

@admin_bp.route('/orders/<order_id>/status', methods=['POST'])
@admin_required
def update_order_status(order_id):
    status = request.form.get('status')
    conn = get_db()
    placeholder = '%s' if hasattr(conn, 'conn') else '?'
    conn.execute(f"UPDATE orders SET order_status = {placeholder} WHERE id = {placeholder}", (status, order_id))
    conn.commit()
    conn.close()
    flash(f'Order {order_id} status updated to {status}', 'success')
    return redirect(url_for('admin.orders'))

@admin_bp.route('/payments')
@admin_required
def payments():
    conn = get_db()
    payments = conn.execute("""
        SELECT 
            id as order_id, 
            COALESCE(NULLIF(razorpay_payment_id, ''), 'PAY_' || SUBSTR(id, 4)) as razorpay_payment_id, 
            COALESCE(NULLIF(payment_method, ''), 'Cash on Delivery') as payment_method, 
            total_amount as amount, 
            COALESCE(NULLIF(payment_status, ''), 'Pending') as payment_status, 
            created_at 
        FROM orders 
        ORDER BY created_at DESC
    """).fetchall()
    conn.close()
    return render_template('admin_payments.html', payments=payments)

@admin_bp.route('/customers')
@admin_required
def customers():
    conn = get_db()
    customers = conn.execute("SELECT id, name, email, mobile, created_at FROM users WHERE role = 'customer' ORDER BY created_at DESC").fetchall()
    conn.close()
    return render_template('admin_customers.html', customers=customers)

@admin_bp.route('/reports')
@admin_required
def reports():
    return render_template('admin_reports.html')
