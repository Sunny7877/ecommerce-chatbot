import sqlite3

conn = sqlite3.connect('database/ecommerce.db')
cur = conn.cursor()
cur.execute("UPDATE products SET image = '/static/images/products/iphone_15.jpg' WHERE name LIKE '%iPhone 15 Pro Max%'")
cur.execute("UPDATE products SET image = '/static/images/products/galaxy_s24.jpg' WHERE name LIKE '%Galaxy S24 Ultra%'")
cur.execute("UPDATE products SET image = '/static/images/products/oneplus_12.jpg' WHERE name LIKE '%OnePlus 12%'")
conn.commit()
conn.close()
print('Local DB updated successfully.')
