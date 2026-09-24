import os
import psycopg2
from dotenv import load_dotenv

# Load the local .env file
load_dotenv()

# Get the Database URL
db_url = os.getenv('DATABASE_URL')
if not db_url:
    print("❌ Error: DATABASE_URL not found in your .env file!")
    exit(1)

print("Connecting to PostgreSQL database...")
try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    print("Dropping old tables if they exist...")
    cur.execute('DROP TABLE IF EXISTS payments CASCADE;')
    cur.execute('DROP TABLE IF EXISTS order_items CASCADE;')
    cur.execute('DROP TABLE IF EXISTS orders CASCADE;')
    cur.execute('DROP TABLE IF EXISTS products CASCADE;')

    print("Creating products table...")
    cur.execute('''
        CREATE TABLE products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            brand VARCHAR(100) NOT NULL,
            category VARCHAR(100) NOT NULL,
            subcategory VARCHAR(100),
            description TEXT,
            price REAL NOT NULL,
            original_price REAL,
            discount_percentage INTEGER DEFAULT 0,
            rating REAL DEFAULT 0,
            review_count INTEGER DEFAULT 0,
            stock INTEGER DEFAULT 0,
            image TEXT,
            badge VARCHAR(50),
            features TEXT
        );
    ''')

    print("Creating orders table...")
    cur.execute('''
        CREATE TABLE orders (
            id VARCHAR(50) PRIMARY KEY,
            razorpay_order_id VARCHAR(100),
            razorpay_payment_id VARCHAR(100),
            razorpay_signature VARCHAR(255),
            name VARCHAR(100),
            email VARCHAR(100),
            phone VARCHAR(20),
            address TEXT,
            city VARCHAR(100),
            state VARCHAR(100),
            pin VARCHAR(20),
            total_amount REAL,
            payment_method VARCHAR(50),
            payment_status VARCHAR(50) DEFAULT 'Pending',
            order_status VARCHAR(50) DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    print("Creating order_items table...")
    cur.execute('''
        CREATE TABLE order_items (
            id SERIAL PRIMARY KEY,
            order_id VARCHAR(50),
            product_id INTEGER,
            quantity INTEGER,
            price REAL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        );
    ''')

    print("Creating payments table...")
    cur.execute('''
        CREATE TABLE payments (
            id SERIAL PRIMARY KEY,
            order_id VARCHAR(50),
            razorpay_payment_id VARCHAR(100),
            razorpay_order_id VARCHAR(100),
            payment_method VARCHAR(50),
            amount REAL,
            status VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders (id)
        );
    ''')

    conn.commit()
    print("✅ All tables created successfully!")
    
    print("Migrating products from local SQLite database...")
    import sqlite3
    sqlite_conn = sqlite3.connect('database/ecommerce.db')
    sqlite_conn.row_factory = sqlite3.Row
    products = sqlite_conn.execute('SELECT * FROM products').fetchall()
    
    for p in products:
        cur.execute('''
            INSERT INTO products (
                id, name, brand, category, subcategory, description, price, 
                original_price, discount_percentage, rating, review_count, stock, 
                image, badge, features
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            p['id'], p['name'], p['brand'], p['category'], p['subcategory'], p['description'], p['price'],
            p['original_price'], p['discount_percentage'], p['rating'], p['review_count'], p['stock'],
            p['image'], p['badge'], p['features']
        ))
    
    conn.commit()
    print(f"✅ Successfully migrated {len(products)} products to PostgreSQL!")

    cur.close()
    conn.close()
    sqlite_conn.close()
    
    print("\n🎉 PostgreSQL Setup Complete! Your database is ready for Render.")

except Exception as e:
    print(f"❌ Database error: {e}")
