import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'ecommerce.db')
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

products = cursor.execute("SELECT id, name, category, subcategory FROM products").fetchall()

for p in products:
    pid = p[0]
    name = p[1].lower()
    cat = p[2].lower()
    sub = p[3].lower() if p[3] else ""
    
    # Determine the best keyword
    keyword = "product"
    if "smartphone" in cat:
        keyword = "smartphone,phone"
    elif "laptop" in cat:
        keyword = "laptop,computer"
    elif "audio" in cat:
        if "earbuds" in sub:
            keyword = "earbuds,earphones"
        elif "speaker" in sub:
            keyword = "speaker"
        else:
            keyword = "headphones"
    elif "watch" in cat:
        keyword = "smartwatch,watch"
    elif "shoes" in cat:
        if "sneaker" in sub:
            keyword = "sneakers,shoes"
        else:
            keyword = "shoes,footwear"
    elif "fashion" in cat:
        if "shirt" in name or "top" in sub:
            keyword = "shirt,clothing"
        elif "jacket" in name:
            keyword = "jacket,clothing"
        elif "jeans" in name or "bottom" in sub:
            keyword = "jeans,clothing"
        else:
            keyword = "fashion,apparel"
    elif "accessories" in cat:
        if "mouse" in name:
            keyword = "computermouse"
        elif "keyboard" in name:
            keyword = "keyboard"
        elif "power" in name:
            keyword = "powerbank"
        else:
            keyword = "gadget"
    elif "home" in cat:
        if "tv" in name:
            keyword = "television,tv"
        elif "monitor" in name:
            keyword = "monitor,screen"
        else:
            keyword = "electronics"

    # Create the unique loremflickr URL using lock=pid
    # This guarantees the same unique image every time it loads.
    url = f"https://loremflickr.com/500/500/{keyword}/all?lock={pid}"
    
    cursor.execute("UPDATE products SET image = ? WHERE id = ?", (url, pid))

conn.commit()
conn.close()

print(f"Successfully updated images for {len(products)} products!")
