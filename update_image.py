import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'database', 'ecommerce.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Update the Google Pixel 8 image with a working URL
new_image_url = 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500&q=80'
cursor.execute("UPDATE products SET image=? WHERE name='Google Pixel 8'", (new_image_url,))

conn.commit()
conn.close()
print("Updated Google Pixel 8 image successfully!")
