import logging
import os
import sys
from datetime import datetime
from flask import Flask, jsonify, render_template_string
import sqlite3

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
DB_PATH = '/app/data/products.db'

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, price REAL NOT NULL, category TEXT NOT NULL)''')
        cursor.execute('SELECT COUNT(*) FROM products')
        if cursor.fetchone()[0] == 0:
            products = [('Laptop Pro 15"', 1299.99, 'Electronics'), ('Wireless Headphones', 199.99, 'Electronics'), ('Coffee Maker', 89.99, 'Appliances'), ('Running Shoes', 129.99, 'Sports'), ('Smartphone', 799.99, 'Electronics')]
            cursor.executemany('INSERT INTO products (name, price, category) VALUES (?, ?, ?)', products)
            conn.commit()
        conn.close()
        return True
    except Exception as e:
        logging.error(f"Database initialization error: {str(e)}")
        return False

init_db()
app = Flask(__name__)
app.secret_key = os.environ.get('APP_SECRET_KEY', 'default-secret-key')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template_string('''<html><head><title>Legacy E-commerce App</title><style>body { font-family: Arial; margin: 40px; } .product { border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 5px; } .error { color: #d32f2f; font-weight: bold; }</style></head><body><h1>🏪 Legacy E-commerce Application</h1><p><strong>Status:</strong> Running on EC2</p><h3>API Endpoints:</h3><ul><li><a href="/api/health">/api/health</a> - Health check</li><li><a href="/api/products">/api/products</a> - Product catalog</li></ul><h3>Sample Products:</h3><div id="products"></div><script>fetch('/api/products').then(r => r.json()).then(data => { const productsHtml = data.products.map(function(p) { return '<div class="product"><h4>' + p.name + '</h4><p>Price: $' + p.price + '</p><p>Category: ' + p.category + '</p></div>'; }).join(''); document.getElementById('products').innerHTML = productsHtml; }).catch(error => { document.getElementById('products').innerHTML = '<p class="error">Error loading products.</p>'; });</script></body></html>''')

@app.route('/api/health')
def health():
    try:
        conn = get_db_connection()
        conn.cursor().execute('SELECT 1 FROM products LIMIT 1')
        conn.close()
        return jsonify({'status': 'healthy', 'version': '1.0.0', 'timestamp': datetime.utcnow().isoformat(), 'database': 'connected'})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e), 'timestamp': datetime.utcnow().isoformat()}), 500

@app.route('/api/products')
def products():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, price, category FROM products')
        rows = cursor.fetchall()
        products = [{'id': row['id'], 'name': row['name'], 'price': row['price'], 'category': row['category']} for row in rows]
        return jsonify({'status': 'success', 'count': len(products), 'products': products})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()
# Test change
