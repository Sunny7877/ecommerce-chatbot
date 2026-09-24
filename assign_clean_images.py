import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'ecommerce.db')

clean_images = {
    "Smartphones": [
        "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500&q=80",
        "https://images.unsplash.com/photo-1605236453806-6ff36851218e?w=500&q=80",
        "https://images.unsplash.com/photo-1592890288551-381c8ab7e57c?w=500&q=80",
        "https://images.unsplash.com/photo-1601784551446-20c9e07cd254?w=500&q=80",
        "https://images.unsplash.com/photo-1580933073521-a249d94943f7?w=500&q=80",
        "https://images.unsplash.com/photo-1598311195666-3d712ce52504?w=500&q=80",
        "https://images.unsplash.com/photo-1546054454-a7e1f53d8396?w=500&q=80",
        "https://images.unsplash.com/photo-1505156868547-9b49f4df4e04?w=500&q=80",
        "https://images.unsplash.com/photo-1603313011101-320f26a4f6f6?w=500&q=80"
    ],
    "Laptops": [
        "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500&q=80",
        "https://images.unsplash.com/photo-1611186871340-1987efaf8938?w=500&q=80",
        "https://images.unsplash.com/photo-1531297172869-4a5c653d1052?w=500&q=80",
        "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=500&q=80",
        "https://images.unsplash.com/photo-1588872657578-c73ce1ac8d22?w=500&q=80",
        "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=500&q=80",
        "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=500&q=80",
        "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500&q=80"
    ],
    "Audio": [
        "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80",
        "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=500&q=80",
        "https://images.unsplash.com/photo-1590658268037-6f11610d48eb?w=500&q=80",
        "https://images.unsplash.com/photo-1606220588913-b3eea4ce4ca8?w=500&q=80",
        "https://images.unsplash.com/photo-1546435736-6e54452140a3?w=500&q=80",
        "https://images.unsplash.com/photo-1613040809024-b4ef7ba99bc3?w=500&q=80"
    ],
    "Smart Watches": [
        "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80",
        "https://images.unsplash.com/photo-1434493789847-2f02b311741c?w=500&q=80",
        "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=500&q=80",
        "https://images.unsplash.com/photo-1508685002907-a95089835824?w=500&q=80",
        "https://images.unsplash.com/photo-1617043786394-f977fa12eddf?w=500&q=80"
    ],
    "Shoes": [
        "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&q=80",
        "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=500&q=80",
        "https://images.unsplash.com/photo-1595950653106-6c9cf1c262f2?w=500&q=80",
        "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?w=500&q=80",
        "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=500&q=80",
        "https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=500&q=80"
    ],
    "Fashion": [
        "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500&q=80",
        "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=500&q=80",
        "https://images.unsplash.com/photo-1542272288118-24900a6f81e3?w=500&q=80",
        "https://images.unsplash.com/photo-1550639524-a829e05f039a?w=500&q=80",
        "https://images.unsplash.com/photo-1618932260643-eee4a2f652a6?w=500&q=80",
        "https://images.unsplash.com/photo-1578587018452-892bacefd3f2?w=500&q=80"
    ],
    "Accessories": [
        "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500&q=80",
        "https://images.unsplash.com/photo-1593640408182-31c70c8268f5?w=500&q=80",
        "https://images.unsplash.com/photo-1587202372778-984dd8da152a?w=500&q=80",
        "https://images.unsplash.com/photo-1615663245857-ac93bb7c90e7?w=500&q=80",
        "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=500&q=80"
    ]
}

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

products = cursor.execute("SELECT id, category FROM products").fetchall()

# Keep track of indices to cycle through available images
category_indices = {k: 0 for k in clean_images.keys()}

for p in products:
    pid = p[0]
    cat = p[1]
    
    # Map Home & Electronics to Accessories for image pool
    pool_key = cat if cat in clean_images else "Accessories"
    
    pool = clean_images[pool_key]
    idx = category_indices[pool_key] % len(pool)
    url = pool[idx]
    category_indices[pool_key] += 1
    
    cursor.execute("UPDATE products SET image = ? WHERE id = ?", (url, pid))

conn.commit()
conn.close()

print("Replaced all images with curated, people-free device photos!")
