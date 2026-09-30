from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def get_db():
    from app import get_db_connection
    return get_db_connection()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'danger')
            return redirect(url_for('auth.admin_login'))
        if session.get('role') != 'admin':
            flash('Unauthorized access.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email = %s" if hasattr(conn, 'conn') else "SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            if user['role'] == 'admin':
                flash('Please use the Admin Portal for admin access.', 'warning')
                return redirect(url_for('auth.login'))
            
            session['user_id'] = user['id']
            session['name'] = user['name']
            session['role'] = user['role']
            flash('Login successful!', 'success')
            return redirect(url_for('customer.dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
            
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.register'))
            
        conn = get_db()
        existing_user = conn.execute("SELECT id FROM users WHERE email = %s" if hasattr(conn, 'conn') else "SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        
        if existing_user:
            conn.close()
            flash('Email already registered. Please log in.', 'danger')
            return redirect(url_for('auth.login'))
            
        password_hash = generate_password_hash(password)
        placeholder = '%s' if hasattr(conn, 'conn') else '?'
        
        conn.execute(f"INSERT INTO users (name, email, mobile, password_hash, role) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, 'customer')",
                     (name, email, mobile, password_hash))
        conn.commit()
        conn.close()
        
        flash('Registration Successful. Your account has been created successfully. Please log in to continue.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('register.html')

@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email = %s AND role = 'admin'" if hasattr(conn, 'conn') else "SELECT * FROM users WHERE email = ? AND role = 'admin'", (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['name'] = user['name']
            session['role'] = user['role']
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid admin credentials.', 'danger')
            
    return render_template('admin_login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('Admin logged out.', 'info')
    return redirect(url_for('auth.admin_login'))
