import os
# Fix for protobuf compatibility on newer Python versions (like Python 3.14)
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import json
import sqlite3
import datetime
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

def get_db_connection():
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        import psycopg2
        conn = psycopg2.connect(db_url, sslmode='require')
        return PostgresWrapper(conn)
    else:
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

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
    order_id = request.json.get('order_id')
    conn = get_db_connection()
    order = conn.execute('SELECT order_status, payment_status, created_at FROM orders WHERE id = ?', (order_id,)).fetchone()
    conn.close()
    if order:
        return jsonify({'success': True, 'status': order['order_status'], 'payment_status': order['payment_status'], 'date': order['created_at']})
    return jsonify({'success': False, 'message': 'Order not found'})

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '').lower()
    
    fallback_responses = {
        'shipping': 'We offer fast delivery within 3-5 business days.',
        'return': 'We have a 7-day easy return policy for all items.',
        'refund': 'Refunds are processed to the original payment method within 3-5 working days.',
        'payment': 'We accept UPI (QR Code & ID), Credit/Debit Cards, Net Banking, Wallets via our secure Razorpay gateway, and Cash on Delivery.',
        'track': 'You can track your order using the Track Order page with your Order ID.'
    }
    
    for key, val in fallback_responses.items():
        if key in user_message and not client:
            return jsonify({'response': val})
            
    conn = get_db_connection()
    products_raw = conn.execute('SELECT id, name, brand, category, price, discount_percentage FROM products LIMIT 150').fetchall()
    conn.close()
    catalog_context = "Products: " + "; ".join([f"[{p['id']}] {p['brand']} {p['name']} - Rs.{p['price']} ({p['discount_percentage']}% off)" for p in products_raw])
    
    if client:
        try:
            prompt = f"""You are an intelligent customer-support chatbot for an e-commerce shopping website. Your role is to help customers solve their shopping-related questions quickly, accurately, and politely.

            AVAILABLE PRODUCT DATA (USE THIS TO RECOMMEND PRODUCTS):
            {catalog_context}

            You can assist customers with:
            - Searching for products by name, category, brand, price, or features
            - Giving product details, prices, discounts, and stock status
            - Recommending products based on budget, needs, and preferences
            - Comparing products
            - Adding, removing, and viewing products in the shopping cart
            - Explaining how to place an order
            - Checking order status and tracking deliveries
            - Explaining shipping charges, delivery time, and delivery-area availability
            - Helping with order cancellation, returns, replacements, and refunds
            - Answering payment questions, failed-payment issues, coupon problems, and cash-on-delivery availability
            - Helping with login, account creation, password reset, saved addresses, and order history
            - Explaining store policies, including delivery, return, refund, privacy, and cancellation policies
            - Directing the customer to customer support when the issue requires human assistance

            Follow these rules:
            1. Greet the customer politely and use friendly, simple language.
            2. Understand the customer's question before answering.
            3. If the question is unclear, ask a short follow-up question.
            4. Give accurate answers using available product, order, cart, account, and policy information. Use markdown links to recommend products: [Product Name](/product/PRODUCT_ID).
            5. Never invent product availability, order status, prices, refund dates, or policy details.
            6. If information is unavailable, say so clearly and offer the next best action.
            7. Ask for an order ID only when required for order, delivery, cancellation, return, or refund queries.
            8. Confirm important actions, such as adding an item to the cart, cancelling an order, or submitting a return request.
            9. Never request or reveal passwords, OTPs, CVV numbers, card PINs, or complete card details.
            10. Protect customer privacy and do not share customer information with anyone else.
            11. If you cannot solve the issue, apologize politely and guide the customer to human support at support@shopease.com.
            12. End every response by asking if the customer needs further help.

            Use this response style:
            - Be concise, clear, and helpful.
            - Give step-by-step instructions when needed.
            - Use bullet points for product lists, comparisons, and procedures.
            - Show prices in ₹ where appropriate.
            - Keep the tone professional and reassuring.

            User Query: {user_message}"""
            
            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt
            )
            return jsonify({'response': response.text})
        except Exception as e:
            print("AI Error:", e)
            return jsonify({'response': "I'm sorry, my AI brain is experiencing high demand right now (Google API is busy). Please try asking again in a few moments, or use the search bar to find products!"})
    
    if 'laptop' in user_message:
        return jsonify({'response': "We have laptops from top brands like Apple, Dell, Lenovo, and ASUS. <a href='/products?category=Laptops'>Check our laptops here!</a>"})
    elif 'phone' in user_message or 'smartphone' in user_message:
        return jsonify({'response': "We offer top iPhones, Samsung Galaxy, OnePlus, and Google Pixel. <a href='/products?category=Smartphones'>Browse Smartphones!</a>"})
    
    return jsonify({'response': "I can help you find products, check prices, track orders, or answer payment questions. What are you looking for today?"})

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
