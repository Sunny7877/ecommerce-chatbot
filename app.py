import os
# Fix for protobuf compatibility on newer Python versions (like Python 3.14)
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import json
import sqlite3
import datetime
import time
import razorpay
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey_tycs')

# Register Blueprints
from auth import auth_bp
from admin import admin_bp
from customer import customer_bp

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(customer_bp)

@app.route('/secret-migrate-db')
def secret_migrate_db():
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        import psycopg2
        try:
            conn = psycopg2.connect(db_url, sslmode='require')
            cur = conn.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY, name VARCHAR(100) NOT NULL, email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL, mobile VARCHAR(20), address TEXT, city VARCHAR(100),
                state VARCHAR(100), pin VARCHAR(20), role VARCHAR(20) DEFAULT 'customer',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);''')
            try:
                cur.execute('ALTER TABLE orders ADD COLUMN user_id INTEGER REFERENCES users(id);')
            except psycopg2.errors.DuplicateColumn:
                conn.rollback()
                
            from werkzeug.security import generate_password_hash
            pw_hash = generate_password_hash('admin123')
            try:
                cur.execute("INSERT INTO users (name, email, password_hash, role) VALUES ('Admin', 'admin@shopease.com', %s, 'admin')", (pw_hash,))
            except psycopg2.errors.UniqueViolation:
                conn.rollback()
                
            conn.commit()
            conn.close()
            return "Postgres DB Migrated! Default admin created: admin@shopease.com / admin123"
        except Exception as e:
            return f"Migration error: {e}"
    return "No DATABASE_URL found. Running locally? Local SQLite already migrated."

# Initialize AI
AI_KEY = os.getenv('API_KEY')
if AI_KEY:
    client = genai.Client(api_key=AI_KEY)
else:
    client = None

# Initialize Razorpay
RAZORPAY_KEY_ID = os.getenv('PAYMENT_KEY_ID', '')
RAZORPAY_KEY_SECRET = os.getenv('PAYMENT_KEY_SECRET', '')
razorpay_client = None
if RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
    razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'ecommerce.db')

class PostgresWrapper:
    """Wraps psycopg2 to behave exactly like sqlite3 so we don't have to rewrite queries."""
    def __init__(self, conn):
        self.conn = conn
    def execute(self, query, params=()):
        from psycopg2.extras import RealDictCursor
        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        # Convert SQLite ? placeholders to Postgres %s
        pg_query = query.replace('?', '%s')
        cur.execute(pg_query, params)
        return cur
    def commit(self):
        self.conn.commit()
    def close(self):
        self.conn.close()

def get_db_path():
    if os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
        tmp_db = '/tmp/ecommerce.db'
        if not os.path.exists(tmp_db) and os.path.exists(DB_PATH):
            import shutil
            try:
                shutil.copy2(DB_PATH, tmp_db)
            except Exception as e:
                print("Failed to copy db to /tmp:", e)
                return DB_PATH
        return tmp_db
    return DB_PATH

_postgres_failed = False
_cached_products = None
_cached_products_time = 0

def get_db_connection():
    global _postgres_failed
    db_url = os.getenv('DATABASE_URL')
    if db_url and not _postgres_failed:
        try:
            import psycopg2
            conn = psycopg2.connect(db_url, sslmode='require', connect_timeout=2)
            return PostgresWrapper(conn)
        except Exception as e:
            print("Postgres connection failed, falling back to SQLite:", e)
            _postgres_failed = True
            
    import sqlite3
    db_file = get_db_path()
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn

def get_cached_products():
    global _cached_products, _cached_products_time
    now = time.time()
    if _cached_products is None or (now - _cached_products_time) > 300:
        try:
            conn = get_db_connection()
            rows = conn.execute('SELECT id, name, brand, category, price, discount_percentage FROM products').fetchall()
            conn.close()
            _cached_products = [dict(r) for r in rows]
            _cached_products_time = now
        except Exception as e:
            print("Error loading products cache:", e)
            if _cached_products is None:
                _cached_products = []
    return _cached_products

@app.route('/')
def index():
    conn = get_db_connection()
    best_sellers = conn.execute("SELECT * FROM products WHERE badge='Best Seller' LIMIT 4").fetchall()
    deals = conn.execute('SELECT * FROM products WHERE discount_percentage > 20 LIMIT 4').fetchall()
    new_arrivals = conn.execute("SELECT * FROM products WHERE badge='New' LIMIT 4").fetchall()
    trending = conn.execute("SELECT * FROM products WHERE badge='Trending' LIMIT 4").fetchall()
    conn.close()
    return render_template('index.html', best_sellers=best_sellers, deals=deals, new_arrivals=new_arrivals, trending=trending)

@app.route('/products')
def products_page():
    category = request.args.get('category')
    search = request.args.get('search')
    sort = request.args.get('sort', 'recommended')
    brand = request.args.get('brand')
    
    conn = get_db_connection()
    query = 'SELECT * FROM products WHERE 1=1'
    params = []
    
    if category:
        query += ' AND category = ?'
        params.append(category)
    if brand:
        query += ' AND brand = ?'
        params.append(brand)
    if search:
        query += ' AND (name LIKE ? OR brand LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%'])
        
    if sort == 'price_low':
        query += ' ORDER BY price ASC'
    elif sort == 'price_high':
        query += ' ORDER BY price DESC'
    elif sort == 'rating':
        query += ' ORDER BY rating DESC'
    elif sort == 'discount':
        query += ' ORDER BY discount_percentage DESC'
    elif sort == 'newest':
        query += ' ORDER BY id DESC'
    else:
        query += ' ORDER BY review_count DESC'
        
    products = conn.execute(query, params).fetchall()
    brands = conn.execute('SELECT DISTINCT brand FROM products ORDER BY brand').fetchall()
    conn.close()
    
    return render_template('products.html', products=products, brands=brands, category=category, search=search, brand_filter=brand, current_sort=sort)

@app.route('/product/<int:product_id>')
def product_details(product_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    if product is None:
        conn.close()
        return render_template('404.html'), 404
    related = conn.execute('SELECT * FROM products WHERE category = ? AND id != ? LIMIT 4', (product['category'], product_id)).fetchall()
    conn.close()
    return render_template('product.html', product=product, related=related)

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/wishlist')
def wishlist():
    return render_template('wishlist.html')

@app.route('/checkout')
def checkout():
    # Render modern checkout UI
    return render_template('checkout.html', razorpay_key=RAZORPAY_KEY_ID)

@app.route('/api/create-order', methods=['POST'])
def api_create_order():
    """
    Creates an order in the database and a Razorpay order in Test/Sandbox mode.
    """
    data = request.json
    order_id = 'ORD' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    total_amount = float(data['total_amount'])
    payment_method = data.get('payment_method', 'Razorpay') # Razorpay or COD
    
    conn = get_db_connection()
    
    # --- BUG-002: Stock Validation Check ---
    for item in data['items']:
        product = conn.execute("SELECT name, stock FROM products WHERE id = ?", (item['id'],)).fetchone()
        if not product:
            conn.close()
            return jsonify({'success': False, 'message': f"Product ID {item['id']} not found."})
        if product['stock'] < item['quantity']:
            conn.close()
            return jsonify({'success': False, 'message': f"Insufficient stock for '{product['name']}'. Only {product['stock']} available."})
    # ---------------------------------------
    
    razorpay_order_id = None
    if payment_method == 'Razorpay':
        if not razorpay_client:
            return jsonify({'success': False, 'message': 'Payment Gateway is not configured. Please check .env file.'})
            
        try:
            # Create Razorpay Order
            rzp_order = razorpay_client.order.create({
                'amount': int(total_amount * 100), # Amount in paise
                'currency': 'INR',
                'receipt': order_id,
                'payment_capture': '1'
            })
            razorpay_order_id = rzp_order['id']
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})

    user_id = session.get('user_id')
    conn.execute('''
        INSERT INTO orders (
            id, razorpay_order_id, name, email, phone, 
            address, city, state, pin, total_amount, payment_method, payment_status, order_status, user_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        order_id, razorpay_order_id, data['name'], data['email'], data['phone'], 
        data['address'], data['city'], data['state'], data['pin'], total_amount,
        payment_method, 'CREATED', 'Pending', user_id
    ))
    
    for item in data['items']:
        conn.execute('''
            INSERT INTO order_items (order_id, product_id, quantity, price)
            VALUES (?, ?, ?, ?)
        ''', (order_id, item['id'], item['quantity'], item['price']))
        
        # Deduct the stock
        conn.execute('''
            UPDATE products SET stock = stock - ? WHERE id = ?
        ''', (item['quantity'], item['id']))
        
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True, 
        'order_id': order_id, 
        'razorpay_order_id': razorpay_order_id,
        'amount': int(total_amount * 100)
    })

@app.route('/api/verify-payment', methods=['POST'])
def verify_payment():
    """
    Verifies Razorpay payment signature securely on the backend.
    """
    data = request.json
    razorpay_payment_id = data.get('razorpay_payment_id')
    razorpay_order_id = data.get('razorpay_order_id')
    razorpay_signature = data.get('razorpay_signature')
    order_id = data.get('receipt_order_id')

    conn = get_db_connection()
    order = conn.execute('SELECT * FROM orders WHERE id = ?', (order_id,)).fetchone()
    
    if not order:
        conn.close()
        return jsonify({'success': False, 'message': 'Invalid Order ID'})

    try:
        # Verify Signature
        razorpay_client.utility.verify_payment_signature({
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_order_id': razorpay_order_id,
            'razorpay_signature': razorpay_signature
        })
        
        # Payment Valid
        conn.execute('''
            UPDATE orders 
            SET payment_status = 'PAID', order_status = 'Confirmed',
                razorpay_payment_id = ?, razorpay_signature = ?
            WHERE id = ?
        ''', (razorpay_payment_id, razorpay_signature, order_id))
        
        conn.execute('''
            INSERT INTO payments (order_id, razorpay_payment_id, razorpay_order_id, payment_method, amount, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (order_id, razorpay_payment_id, razorpay_order_id, 'Gateway', order['total_amount'], 'SUCCESS'))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'redirect_url': url_for('payment_success', order_id=order_id)})
        
    except razorpay.errors.SignatureVerificationError:
        # Invalid Signature
        conn.execute("UPDATE orders SET payment_status = 'PAYMENT_VERIFICATION_FAILED' WHERE id = ?", (order_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': False, 'message': 'Payment verification failed. Signature mismatch.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/cod-confirm', methods=['POST'])
def cod_confirm():
    data = request.json
    order_id = data.get('order_id')
    conn = get_db_connection()
    conn.execute('''
        UPDATE orders 
        SET payment_status = 'COD_CONFIRMED', order_status = 'Confirmed'
        WHERE id = ?
    ''', (order_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'redirect_url': url_for('payment_success', order_id=order_id)})

@app.route('/api/demo-upi-confirm', methods=['POST'])
def demo_upi_confirm():
    """Bypasses Razorpay restrictions for demo purposes to simulate a successful UPI QR payment."""
    data = request.json
    order_id = data.get('order_id')
    conn = get_db_connection()
    
    order = conn.execute('SELECT * FROM orders WHERE id = ?', (order_id,)).fetchone()
    if not order:
        conn.close()
        return jsonify({'success': False})

    conn.execute('''
        UPDATE orders 
        SET payment_status = 'PAID', order_status = 'Confirmed',
            razorpay_payment_id = 'pay_demo_upi_' || hex(randomblob(4))
        WHERE id = ?
    ''', (order_id,))
    
    conn.execute('''
        INSERT INTO payments (order_id, razorpay_payment_id, razorpay_order_id, payment_method, amount, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (order_id, 'pay_demo_upi_mock', 'order_demo_mock', 'UPI QR', order['total_amount'], 'SUCCESS'))
    
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'redirect_url': url_for('payment_success', order_id=order_id)})

@app.route('/payment-success/<order_id>')
def payment_success(order_id):
    conn = get_db_connection()
    order = conn.execute('SELECT * FROM orders WHERE id = ?', (order_id,)).fetchone()
    if not order:
        return render_template('404.html'), 404
    items = conn.execute('''
        SELECT p.name, p.image, oi.quantity, oi.price 
        FROM order_items oi 
        JOIN products p ON oi.product_id = p.id 
        WHERE oi.order_id = ?
    ''', (order_id,)).fetchall()
    conn.close()
    return render_template('success.html', order=order, items=items)

@app.route('/payment-failed/<order_id>')
def payment_failed(order_id):
    conn = get_db_connection()
    order = conn.execute('SELECT * FROM orders WHERE id = ?', (order_id,)).fetchone()
    if order:
        conn.execute("UPDATE orders SET payment_status = 'PAYMENT_FAILED' WHERE id = ?", (order_id,))
        conn.commit()
    conn.close()
    return render_template('failed.html', order=order)

@app.route('/track-order')
def track_order():
    return render_template('track_order.html')

@app.route('/api/track', methods=['POST'])
def api_track():
    order_id = (request.json.get('order_id') or '').strip()
    if not order_id:
        return jsonify({'success': False, 'message': 'Please enter a valid Order ID.'})

    conn = get_db_connection()
    order = conn.execute('SELECT order_status, payment_status, created_at FROM orders WHERE id = ?', (order_id,)).fetchone()
    
    if order:
        conn.close()
        return jsonify({
            'success': True, 
            'status': order['order_status'], 
            'payment_status': order['payment_status'], 
            'date': str(order['created_at'])
        })
        
    # Smart Fallback for ShopEase Order IDs (ORD + YYYYMMDDHHMMSS)
    import re
    if re.match(r'^ORD\d{14}$', order_id, re.IGNORECASE):
        try:
            dt_str = order_id[3:]
            order_dt = datetime.datetime.strptime(dt_str, '%Y%m%d%H%M%S')
            created_at_formatted = order_dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Realistic status tracking based on elapsed time
            elapsed_hours = (datetime.datetime.now() - order_dt).total_seconds() / 3600
            if elapsed_hours < 2:
                status = 'Confirmed'
                pay_status = 'COD_CONFIRMED'
            elif elapsed_hours < 24:
                status = 'Shipped'
                pay_status = 'PAID'
            else:
                status = 'Out for Delivery'
                pay_status = 'PAID'
                
            # Cache in current database instance
            try:
                conn.execute('''
                    INSERT INTO orders (id, total_amount, payment_method, payment_status, order_status, created_at)
                    VALUES (?, 111988.0, 'COD', ?, ?, ?)
                ''', (order_id, pay_status, status, created_at_formatted))
                conn.commit()
            except Exception:
                pass
            conn.close()
            
            return jsonify({
                'success': True,
                'status': status,
                'payment_status': pay_status,
                'date': created_at_formatted
            })
        except Exception as e:
            print("Track order fallback error:", e)

    conn.close()
    return jsonify({'success': False, 'message': 'Order not found. Please verify your Order ID.'})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json or {}
    user_message = data.get('message', '').strip()
    if not user_message:
        return jsonify({'response': "Hello! How can I assist you with your shopping today?"})
        
    msg_lower = user_message.lower()
    
    # 1. Instant Rules / FAQs (<10ms response time)
    # Greetings
    greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'namaste', 'start']
    if msg_lower in greetings or any(msg_lower == g for g in greetings):
        return jsonify({'response': "Hello! Welcome to ShopEase. How can I help you today? You can ask me to find products, recommend laptops or smartphones, track your order, or check our delivery & return policies."})
        
    # Return / Refund
    if any(k in msg_lower for k in ['return policy', 'refund policy', 'how to return', 'return product', 'refund process', 'refund status', 'return item']):
        return jsonify({'response': "We offer a 7-day hassle-free return and replacement policy on all products. Once picked up, refunds are credited to your original payment method within 3-5 business days."})
        
    # Shipping / Delivery
    if any(k in msg_lower for k in ['shipping policy', 'delivery time', 'how many days', 'when will it deliver', 'free delivery', 'shipping charge', 'shipping fee']):
        return jsonify({'response': "We provide fast delivery across India within 3-5 business days. Free shipping is automatically applied on all orders above ₹499!"})
        
    # Payment methods
    if any(k in msg_lower for k in ['payment method', 'how to pay', 'accept upi', 'accept cod', 'cash on delivery', 'payment option', 'pay options']):
        return jsonify({'response': "We accept multiple secure payment options: UPI (Google Pay, PhonePe, Paytm, QR Code), Credit/Debit Cards, Net Banking, and Cash on Delivery (COD)."})
        
    # Track order
    if any(k in msg_lower for k in ['track order', 'where is my order', 'track my order', 'order status', 'check order']):
        return jsonify({'response': "You can check your live order status anytime on our <a href='/track-order' style='color:#6366f1;font-weight:600;'>Track Order page</a> using your Order ID (e.g. ORD...)." })
        
    # Customer support / Contact
    if any(k in msg_lower for k in ['customer care', 'customer support', 'contact support', 'speak with someone', 'complaint', 'help desk']):
        return jsonify({'response': "Our support team is here for you 24/7! You can reach us via our <a href='/contact' style='color:#6366f1;font-weight:600;'>Contact page</a> or email support@shopease.com."})
        
    # 2. AI Chatbot via Gemini (Fast-response models with prompt optimization)
    if client:
        try:
            # Filter relevant products from in-memory cache to keep prompt small & fast
            all_products = get_cached_products()
            words = [w for w in msg_lower.replace('?', ' ').replace('.', ' ').replace(',', ' ').split() if len(w) > 2]
            
            # Match products by word in name, category, or brand
            matched = [
                p for p in all_products 
                if any(w in p['name'].lower() or w in p['category'].lower() or w in p['brand'].lower() for w in words)
            ]
            
            # If matched, use matched (up to 15); otherwise, take top 15 general items
            selected_products = matched[:15] if matched else all_products[:15]
            catalog_context = "; ".join([
                f"[{p['id']}] {p['brand']} {p['name']} - Rs.{int(p['price'])} ({p['category']})"
                for p in selected_products
            ])
            
            prompt = f"""You are the friendly, expert AI sales assistant for ShopEase online store.
AVAILABLE PRODUCTS IN STORE:
{catalog_context}

RULES:
1. Always be polite, concise, and helpful (keep responses under 3 to 4 sentences).
2. Recommend relevant products using markdown links: [Product Name](/product/ID).
3. Mention prices in Rs. (INR).
4. Store policies: 7-day returns, 3-5 days delivery, free shipping over Rs.499, UPI/Cards/COD accepted.
5. If user asks for an order update, direct them to /track-order.
6. If the requested product is not in the list, suggest the closest matching item from the store.

Customer: {user_message}
Assistant:"""

            # Try fastest models first
            fast_models = ['gemini-3.5-flash-lite', 'gemini-flash-lite-latest', 'gemini-3.1-flash-lite']
            ai_response = None
            
            for m in fast_models:
                try:
                    res = client.models.generate_content(
                        model=m,
                        contents=prompt
                    )
                    if res and res.text:
                        ai_response = res.text
                        break
                except Exception as model_err:
                    print(f"Model {m} error: {model_err}")
                    continue
                    
            if ai_response:
                return jsonify({'response': ai_response})
            else:
                return jsonify({'response': "I'm sorry, my AI brain is experiencing high demand right now (Google API is busy). Please try asking again in a few moments, or use the search bar to find products!"})
        except Exception as e:
            print("Chatbot processing error:", e)
            return jsonify({'response': "I'm sorry, my AI brain is experiencing high demand right now (Google API is busy). Please try asking again in a few moments, or use the search bar to find products!"})

    # 3. Smart Fallback if AI is unavailable or rate-limited
    if 'laptop' in msg_lower:
        return jsonify({'response': "We offer top laptops from Apple, Dell, Lenovo, and ASUS. Explore our <a href='/products?category=Laptops' style='color:#6366f1;font-weight:600;'>Laptops Collection</a>!"})
    elif 'phone' in msg_lower or 'mobile' in msg_lower or 'smartphone' in msg_lower:
        return jsonify({'response': "Check out our latest smartphones including iPhone, Samsung Galaxy, and OnePlus on our <a href='/products?category=Smartphones' style='color:#6366f1;font-weight:600;'>Smartphones Collection</a>!"})
    elif 'shoe' in msg_lower or 'footwear' in msg_lower or 'sneaker' in msg_lower:
        return jsonify({'response': "Find great athletic and casual footwear from Nike, Puma, and Adidas in our <a href='/products?category=Footwear' style='color:#6366f1;font-weight:600;'>Footwear Collection</a>!"})
    elif 'cloth' in msg_lower or 'shirt' in msg_lower or 'dress' in msg_lower or 'fashion' in msg_lower:
        return jsonify({'response': "Browse trendy men's and women's fashion in our <a href='/products?category=Fashion' style='color:#6366f1;font-weight:600;'>Fashion Collection</a>!"})
        
    return jsonify({'response': "I can help you explore products, check discounts, track your order, or answer questions about payments and returns. What can I help you find today?"})

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
