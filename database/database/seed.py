import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'ecommerce.db')

def seed_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Ensure table exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            brand TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            discount REAL DEFAULT 0,
            rating REAL DEFAULT 0,
            stock INTEGER DEFAULT 0,
            image TEXT
        )
    ''')
    
    # Check if data exists
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] > 0:
        print("Database already seeded.")
        conn.close()
        return

    products = [
        ("iPhone 15 Pro", "Smartphones", "Apple", "The ultimate iPhone with titanium design.", 134900, 5, 4.8, 50, "https://images.unsplash.com/photo-1696446701796-da61225697cc?w=500&q=80"),
        ("Samsung Galaxy S24 Ultra", "Smartphones", "Samsung", "AI-powered smartphone with S Pen.", 129999, 10, 4.7, 45, "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=500&q=80"),
        ("OnePlus 12", "Smartphones", "OnePlus", "Smooth beyond belief.", 64999, 0, 4.6, 60, "https://images.unsplash.com/photo-1678911820864-e2c567c655d7?w=500&q=80"),
        ("Google Pixel 8", "Smartphones", "Google", "The Google phone with advanced AI camera.", 75999, 15, 4.5, 30, "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500&q=80"),
        
        ("HP Pavilion 15", "Laptops", "HP", "High performance laptop for students and professionals.", 55000, 10, 4.2, 20, "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=500&q=80"),
        ("Dell XPS 13", "Laptops", "Dell", "Premium thin and light laptop.", 115000, 5, 4.8, 15, "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=500&q=80"),
        ("Lenovo IdeaPad Slim 3", "Laptops", "Lenovo", "Best budget laptop for college.", 35000, 12, 4.1, 40, "https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=500&q=80"),
        ("ASUS ROG Zephyrus", "Laptops", "ASUS", "Ultimate gaming powerhouse.", 145000, 8, 4.9, 10, "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=500&q=80"),

        ("Sony WH-1000XM5", "Headphones", "Sony", "Industry leading noise canceling.", 29990, 10, 4.8, 25, "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=500&q=80"),
        ("JBL Tune 710BT", "Headphones", "JBL", "Pure bass over-ear headphones.", 4499, 20, 4.3, 100, "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=500&q=80"),
        ("boAt Rockerz 450", "Headphones", "Boat", "Wireless bluetooth headphones.", 1499, 50, 4.0, 200, "https://images.unsplash.com/photo-1612222869049-d8ec83637a3c?w=500&q=80"),
        ("Noise One", "Headphones", "Noise", "Comfortable everyday headphones.", 1299, 40, 3.9, 150, "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80"),

        ("Apple Watch Series 9", "Smart Watches", "Apple", "Advanced health sensors and display.", 41900, 5, 4.7, 30, "https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=500&q=80"),
        ("Samsung Galaxy Watch 6", "Smart Watches", "Samsung", "Fitness tracking and sleep monitoring.", 29999, 15, 4.6, 40, "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=500&q=80"),
        ("Noise ColorFit Pro", "Smart Watches", "Noise", "Affordable fitness smartwatch.", 2999, 60, 4.1, 100, "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=500&q=80"),
        
        ("Nike Air Zoom", "Shoes", "Nike", "Comfortable running shoes.", 8995, 10, 4.5, 60, "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&q=80"),
        ("Puma Smash v2", "Shoes", "Puma", "Classic everyday casual shoes.", 3499, 30, 4.2, 80, "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=500&q=80"),

        ("Logitech MX Master 3S", "Accessories", "Logitech", "Ergonomic wireless mouse.", 9999, 5, 4.8, 20, "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500&q=80"),
        ("Keychron K2", "Accessories", "Keychron", "Mechanical wireless keyboard.", 7500, 10, 4.7, 15, "https://images.unsplash.com/photo-1595225476474-87563907a212?w=500&q=80"),
        ("Mi Power Bank 20000mAh", "Accessories", "Xiaomi", "Fast charging power bank.", 2199, 15, 4.4, 200, "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=500&q=80")
    ]
    
    cursor.executemany('''
        INSERT INTO products (name, category, brand, description, price, discount, rating, stock, image)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', products)
    
    conn.commit()
    conn.close()
    print("Database seeded successfully with 20 sample products.")

if __name__ == '__main__':
    seed_data()
