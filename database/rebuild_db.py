import sqlite3
import os
import random

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'ecommerce.db')

def rebuild():
    print(f"Rebuilding database at {DB_PATH}...")
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH) 
    
    # Ensure dir exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    
    conn.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            brand TEXT NOT NULL,
            category TEXT NOT NULL,
            subcategory TEXT,
            description TEXT,
            price REAL NOT NULL,
            original_price REAL,
            discount_percentage INTEGER DEFAULT 0,
            rating REAL DEFAULT 0,
            review_count INTEGER DEFAULT 0,
            stock INTEGER DEFAULT 0,
            image TEXT,
            badge TEXT,
            features TEXT
        )
    ''')
    
    conn.execute('''
        CREATE TABLE orders (
            id TEXT PRIMARY KEY,
            razorpay_order_id TEXT,
            razorpay_payment_id TEXT,
            razorpay_signature TEXT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            pin TEXT NOT NULL,
            total_amount REAL NOT NULL,
            payment_method TEXT,
            payment_status TEXT DEFAULT 'CREATED',
            order_status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
            product_id INTEGER,
            quantity INTEGER,
            price REAL,
            FOREIGN KEY(order_id) REFERENCES orders(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    ''')
    conn.execute('''
        CREATE TABLE payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
            razorpay_payment_id TEXT,
            razorpay_order_id TEXT,
            payment_method TEXT,
            amount REAL,
            currency TEXT DEFAULT 'INR',
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(order_id) REFERENCES orders(id)
        )
    ''')

    clean_images = {
        "Smartphones": [
            "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500&q=80",
            "https://images.unsplash.com/photo-1605236453806-6ff36851218e?w=500&q=80",
            "https://images.unsplash.com/photo-1505156868547-9b49f4df4e04?w=500&q=80",
            "https://images.unsplash.com/photo-1603313011101-320f26a4f6f6?w=500&q=80"
        ],
        "Laptops": [
            "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500&q=80",
            "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=500&q=80",
            "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=500&q=80",
            "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=500&q=80",
            "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500&q=80"
        ],
        "Audio": [
            "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80",
            "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=500&q=80",
            "https://images.unsplash.com/photo-1613040809024-b4ef7ba99bc3?w=500&q=80"
        ],
        "Smart Watches": [
            "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80",
            "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=500&q=80",
            "https://images.unsplash.com/photo-1617043786394-f977fa12eddf?w=500&q=80"
        ],
        "Shoes": [
            "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&q=80",
            "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=500&q=80",
            "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?w=500&q=80",
            "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=500&q=80",
            "https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=500&q=80"
        ],
        "Fashion": [
            "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500&q=80",
            "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=500&q=80",
            "https://images.unsplash.com/photo-1618932260643-eee4a2f652a6?w=500&q=80",
            "https://images.unsplash.com/photo-1578587018452-892bacefd3f2?w=500&q=80"
        ],
        "Accessories": [
            "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500&q=80",
            "https://images.unsplash.com/photo-1593640408182-31c70c8268f5?w=500&q=80",
            "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=500&q=80"
        ]
    }
    
    category_indices = {k: 0 for k in clean_images.keys()}

    final_products = []
    for p in base_products:
        name, brand, cat, subcat, price, orig_price, badge = p
        
        pool_key = cat if cat in clean_images else "Accessories"
        pool = clean_images[pool_key]
        idx = category_indices[pool_key] % len(pool)
        img = pool[idx]
        category_indices[pool_key] += 1
        desc = f"Experience premium quality with the {brand} {name}. Designed for maximum performance, incredible durability, and everyday use."
        feat = "Premium Build Quality | 1 Year Manufacturer Warranty | Fast Reliable Shipping | Easy 7-Day Returns"
        
        discount_pct = int(((orig_price - price) / orig_price) * 100) if orig_price > price else 0
        rating = round(random.uniform(4.1, 4.9), 1)
        reviews = random.randint(120, 4500)
        stock = random.randint(5, 150)
        if "Limited" in badge: stock = random.randint(1, 10)
        
        final_products.append((name, brand, cat, subcat, desc, price, orig_price, discount_pct, rating, reviews, stock, img, badge, feat))

    cursor = conn.cursor()
    cursor.executemany('''
        INSERT INTO products (name, brand, category, subcategory, description, price, original_price, discount_percentage, rating, review_count, stock, image, badge, features)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', final_products)
    
    conn.commit()
    conn.close()
    print(f"Rebuilt Database with {len(final_products)} products successfully!")

if __name__ == '__main__':
    rebuild()
