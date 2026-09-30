from flask import Blueprint, render_template, session, redirect, url_for
from auth import login_required, get_db

customer_bp = Blueprint('customer', __name__, url_prefix='/customer')

@customer_bp.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    placeholder = '%s' if hasattr(conn, 'conn') else '?'
    orders = conn.execute(f"SELECT * FROM orders WHERE user_id = {placeholder} ORDER BY created_at DESC LIMIT 5", (session['user_id'],)).fetchall()
    conn.close()
    return render_template('customer_dashboard.html', orders=orders)

@customer_bp.route('/orders')
@login_required
def my_orders():
    conn = get_db()
    placeholder = '%s' if hasattr(conn, 'conn') else '?'
    orders = conn.execute(f"SELECT * FROM orders WHERE user_id = {placeholder} ORDER BY created_at DESC", (session['user_id'],)).fetchall()
    conn.close()
    return render_template('my_orders.html', orders=orders)

@customer_bp.route('/profile')
@login_required
def profile():
    conn = get_db()
    placeholder = '%s' if hasattr(conn, 'conn') else '?'
    user = conn.execute(f"SELECT * FROM users WHERE id = {placeholder}", (session['user_id'],)).fetchone()
    conn.close()
    return render_template('customer_profile.html', user=user)
