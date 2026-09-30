import os

def create_template(filename, content):
    path = os.path.join('templates', filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

templates = {}

templates['customer_dashboard.html'] = '''{% extends 'base.html' %}
{% block title %}My Dashboard - ShopEase AI{% endblock %}
{% block content %}
<div class="container py-5">
    <div class="row">
        <div class="col-md-3 mb-4">
            <div class="list-group shadow-sm border-0">
                <a href="{{ url_for('customer.dashboard') }}" class="list-group-item list-group-item-action active"><i class="bi bi-grid me-2"></i> Dashboard</a>
                <a href="{{ url_for('customer.my_orders') }}" class="list-group-item list-group-item-action"><i class="bi bi-box-seam me-2"></i> My Orders</a>
                <a href="{{ url_for('track_order') }}" class="list-group-item list-group-item-action"><i class="bi bi-geo-alt me-2"></i> Track Order</a>
                <a href="{{ url_for('customer.profile') }}" class="list-group-item list-group-item-action"><i class="bi bi-person me-2"></i> Profile</a>
                <a href="{{ url_for('auth.logout') }}" class="list-group-item list-group-item-action text-danger"><i class="bi bi-box-arrow-right me-2"></i> Logout</a>
            </div>
        </div>
        <div class="col-md-9">
            <h3 class="mb-4">Welcome back, {{ session.name }}!</h3>
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            <div class="row g-4 mb-4">
                <div class="col-md-6">
                    <div class="card shadow-sm border-0 bg-primary text-white h-100">
                        <div class="card-body">
                            <h5>Recent Orders</h5>
                            <p class="display-6">{{ orders|length }}</p>
                            <a href="{{ url_for('customer.my_orders') }}" class="text-white">View All Orders &rarr;</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''

templates['my_orders.html'] = '''{% extends 'base.html' %}
{% block title %}My Orders - ShopEase AI{% endblock %}
{% block content %}
<div class="container py-5">
    <div class="row">
        <div class="col-md-3 mb-4">
            <div class="list-group shadow-sm border-0">
                <a href="{{ url_for('customer.dashboard') }}" class="list-group-item list-group-item-action"><i class="bi bi-grid me-2"></i> Dashboard</a>
                <a href="{{ url_for('customer.my_orders') }}" class="list-group-item list-group-item-action active"><i class="bi bi-box-seam me-2"></i> My Orders</a>
                <a href="{{ url_for('track_order') }}" class="list-group-item list-group-item-action"><i class="bi bi-geo-alt me-2"></i> Track Order</a>
                <a href="{{ url_for('customer.profile') }}" class="list-group-item list-group-item-action"><i class="bi bi-person me-2"></i> Profile</a>
                <a href="{{ url_for('auth.logout') }}" class="list-group-item list-group-item-action text-danger"><i class="bi bi-box-arrow-right me-2"></i> Logout</a>
            </div>
        </div>
        <div class="col-md-9">
            <h3 class="mb-4">My Orders</h3>
            {% if orders %}
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead class="table-light">
                            <tr>
                                <th>Order ID</th>
                                <th>Date</th>
                                <th>Total Amount</th>
                                <th>Payment</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for order in orders %}
                            <tr>
                                <td class="fw-bold">{{ order.id }}</td>
                                <td>{{ order.created_at[:10] }}</td>
                                <td>₹{{ order.total_amount }}</td>
                                <td><span class="badge bg-{{ 'success' if order.payment_status == 'PAID' else 'secondary' }}">{{ order.payment_status }}</span></td>
                                <td><span class="badge bg-{{ 'primary' if order.order_status == 'Delivered' else 'info' }}">{{ order.order_status }}</span></td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            {% else %}
                <div class="alert alert-info">You have not placed any orders yet. <a href="{{ url_for('products_page') }}">Start shopping!</a></div>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}'''

templates['customer_profile.html'] = '''{% extends 'base.html' %}
{% block title %}My Profile - ShopEase AI{% endblock %}
{% block content %}
<div class="container py-5">
    <div class="row">
        <div class="col-md-3 mb-4">
            <div class="list-group shadow-sm border-0">
                <a href="{{ url_for('customer.dashboard') }}" class="list-group-item list-group-item-action"><i class="bi bi-grid me-2"></i> Dashboard</a>
                <a href="{{ url_for('customer.my_orders') }}" class="list-group-item list-group-item-action"><i class="bi bi-box-seam me-2"></i> My Orders</a>
                <a href="{{ url_for('track_order') }}" class="list-group-item list-group-item-action"><i class="bi bi-geo-alt me-2"></i> Track Order</a>
                <a href="{{ url_for('customer.profile') }}" class="list-group-item list-group-item-action active"><i class="bi bi-person me-2"></i> Profile</a>
                <a href="{{ url_for('auth.logout') }}" class="list-group-item list-group-item-action text-danger"><i class="bi bi-box-arrow-right me-2"></i> Logout</a>
            </div>
        </div>
        <div class="col-md-9">
            <h3 class="mb-4">My Profile</h3>
            <div class="card shadow-sm border-0">
                <div class="card-body p-4">
                    <p><strong>Name:</strong> {{ user.name }}</p>
                    <p><strong>Email:</strong> {{ user.email }}</p>
                    <p><strong>Mobile:</strong> {{ user.mobile }}</p>
                    <p><strong>Role:</strong> <span class="badge bg-secondary">{{ user.role }}</span></p>
                    <p><strong>Member Since:</strong> {{ user.created_at[:10] }}</p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''

templates['admin_dashboard.html'] = '''{% extends 'base.html' %}
{% block title %}Admin Dashboard - ShopEase AI{% endblock %}
{% block content %}
<div class="container-fluid py-4">
    <div class="row">
        <div class="col-md-2 mb-4">
            <div class="list-group shadow-sm border-0">
                <a href="{{ url_for('admin.dashboard') }}" class="list-group-item list-group-item-action active">Dashboard</a>
                <a href="{{ url_for('admin.products') }}" class="list-group-item list-group-item-action">Products</a>
                <a href="{{ url_for('admin.inventory') }}" class="list-group-item list-group-item-action">Inventory</a>
                <a href="{{ url_for('admin.orders') }}" class="list-group-item list-group-item-action">Orders</a>
                <a href="{{ url_for('admin.payments') }}" class="list-group-item list-group-item-action">Payments</a>
                <a href="{{ url_for('admin.customers') }}" class="list-group-item list-group-item-action">Customers</a>
                <a href="{{ url_for('admin.reports') }}" class="list-group-item list-group-item-action">Reports</a>
            </div>
        </div>
        <div class="col-md-10">
            <h3 class="mb-4">Admin Dashboard</h3>
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            <div class="row g-4 mb-4">
                <div class="col-md-3">
                    <div class="card bg-primary text-white shadow border-0 h-100">
                        <div class="card-body">
                            <h6>Total Sales</h6>
                            <h3>₹{{ stats.total_sales }}</h3>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-success text-white shadow border-0 h-100">
                        <div class="card-body">
                            <h6>Total Orders</h6>
                            <h3>{{ stats.total_orders }}</h3>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-info text-white shadow border-0 h-100">
                        <div class="card-body">
                            <h6>Customers</h6>
                            <h3>{{ stats.total_customers }}</h3>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-danger text-white shadow border-0 h-100">
                        <div class="card-body">
                            <h6>Pending / Low Stock</h6>
                            <h3>{{ stats.pending_orders }} / {{ stats.low_stock }}</h3>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="card shadow border-0">
                <div class="card-header bg-white fw-bold py-3">Recent Orders</div>
                <div class="card-body p-0">
                    <div class="table-responsive">
                        <table class="table table-hover mb-0">
                            <thead class="table-light">
                                <tr>
                                    <th>Order ID</th>
                                    <th>Payment Status</th>
                                    <th>Order Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for order in recent_orders %}
                                <tr>
                                    <td>{{ order.id }}</td>
                                    <td>{{ order.payment_status }}</td>
                                    <td>{{ order.order_status }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''

templates['admin_products.html'] = '''{% extends 'base.html' %}
{% block title %}Manage Products - Admin{% endblock %}
{% block content %}
<div class="container-fluid py-4">
    <div class="row">
        <div class="col-md-2 mb-4">
            <div class="list-group shadow-sm border-0">
                <a href="{{ url_for('admin.dashboard') }}" class="list-group-item list-group-item-action">Dashboard</a>
                <a href="{{ url_for('admin.products') }}" class="list-group-item list-group-item-action active">Products</a>
                <a href="{{ url_for('admin.inventory') }}" class="list-group-item list-group-item-action">Inventory</a>
                <a href="{{ url_for('admin.orders') }}" class="list-group-item list-group-item-action">Orders</a>
                <a href="{{ url_for('admin.payments') }}" class="list-group-item list-group-item-action">Payments</a>
                <a href="{{ url_for('admin.customers') }}" class="list-group-item list-group-item-action">Customers</a>
            </div>
        </div>
        <div class="col-md-10">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h3>Manage Products</h3>
                <a href="{{ url_for('admin.add_product') }}" class="btn btn-primary"><i class="bi bi-plus-lg"></i> Add Product</a>
            </div>
            <div class="card shadow border-0">
                <div class="card-body p-0">
                    <div class="table-responsive">
                        <table class="table table-hover align-middle mb-0">
                            <thead class="table-light">
                                <tr>
                                    <th>ID</th>
                                    <th>Image</th>
                                    <th>Name</th>
                                    <th>Category</th>
                                    <th>Price</th>
                                    <th>Stock</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for product in products %}
                                <tr>
                                    <td>{{ product.id }}</td>
                                    <td><img src="{{ product.image }}" width="50" class="rounded"></td>
                                    <td>{{ product.name }}</td>
                                    <td>{{ product.category }}</td>
                                    <td>₹{{ product.price }}</td>
                                    <td>{{ product.stock }}</td>
                                    <td>
                                        <button class="btn btn-sm btn-outline-secondary">Edit</button>
                                        <button class="btn btn-sm btn-outline-danger">Delete</button>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''

templates['admin_add_product.html'] = '''{% extends 'base.html' %}
{% block title %}Add Product - Admin{% endblock %}
{% block content %}
<div class="container py-4">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <h3 class="mb-4">Add New Product</h3>
            <div class="card shadow border-0">
                <div class="card-body p-4">
                    <form action="{{ url_for('admin.add_product') }}" method="POST">
                        <div class="row">
                            <div class="col-md-12 mb-3">
                                <label class="form-label fw-bold">Product Name</label>
                                <input type="text" name="name" class="form-control" required>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="form-label fw-bold">Brand</label>
                                <input type="text" name="brand" class="form-control" required>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="form-label fw-bold">Category</label>
                                <input type="text" name="category" class="form-control" required>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="form-label fw-bold">Price (₹)</label>
                                <input type="number" name="price" class="form-control" required>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="form-label fw-bold">Stock</label>
                                <input type="number" name="stock" class="form-control" value="0" required>
                            </div>
                            <div class="col-md-12 mb-3">
                                <label class="form-label fw-bold">Image URL</label>
                                <input type="text" name="image" class="form-control">
                            </div>
                            <div class="col-md-12 mb-3">
                                <label class="form-label fw-bold">Badge (e.g., Best Seller)</label>
                                <input type="text" name="badge" class="form-control">
                            </div>
                            <div class="col-md-12 mb-4">
                                <label class="form-label fw-bold">Description</label>
                                <textarea name="description" class="form-control" rows="3"></textarea>
                            </div>
                        </div>
                        <button type="submit" class="btn btn-primary">Add Product</button>
                        <a href="{{ url_for('admin.products') }}" class="btn btn-secondary">Cancel</a>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''

templates['admin_inventory.html'] = '''{% extends 'base.html' %}
{% block title %}Inventory - Admin{% endblock %}
{% block content %}
<div class="container-fluid py-4">
    <div class="row">
        <div class="col-md-2 mb-4">
            <div class="list-group shadow-sm border-0">
                <a href="{{ url_for('admin.dashboard') }}" class="list-group-item list-group-item-action">Dashboard</a>
                <a href="{{ url_for('admin.products') }}" class="list-group-item list-group-item-action">Products</a>
                <a href="{{ url_for('admin.inventory') }}" class="list-group-item list-group-item-action active">Inventory</a>
                <a href="{{ url_for('admin.orders') }}" class="list-group-item list-group-item-action">Orders</a>
                <a href="{{ url_for('admin.payments') }}" class="list-group-item list-group-item-action">Payments</a>
                <a href="{{ url_for('admin.customers') }}" class="list-group-item list-group-item-action">Customers</a>
            </div>
        </div>
        <div class="col-md-10">
            <h3 class="mb-4">Inventory Management</h3>
            <div class="card shadow border-0">
                <div class="card-body p-0">
                    <div class="table-responsive">
                        <table class="table table-hover align-middle mb-0">
                            <thead class="table-light">
                                <tr>
                                    <th>ID</th>
                                    <th>Product Name</th>
                                    <th>Current Stock</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for product in products %}
                                <tr>
                                    <td>{{ product.id }}</td>
                                    <td>{{ product.name }}</td>
                                    <td>{{ product.stock }}</td>
                                    <td>
                                        {% if product.stock == 0 %}
                                            <span class="badge bg-danger">OUT OF STOCK</span>
                                        {% elif product.stock < 10 %}
                                            <span class="badge bg-warning text-dark">LOW STOCK</span>
                                        {% else %}
                                            <span class="badge bg-success">IN STOCK</span>
                                        {% endif %}
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''

templates['admin_orders.html'] = '''{% extends 'base.html' %}
{% block title %}Manage Orders - Admin{% endblock %}
{% block content %}
<div class="container-fluid py-4">
    <div class="row">
        <div class="col-md-2 mb-4">
            <div class="list-group shadow-sm border-0">
                <a href="{{ url_for('admin.dashboard') }}" class="list-group-item list-group-item-action">Dashboard</a>
                <a href="{{ url_for('admin.products') }}" class="list-group-item list-group-item-action">Products</a>
                <a href="{{ url_for('admin.inventory') }}" class="list-group-item list-group-item-action">Inventory</a>
                <a href="{{ url_for('admin.orders') }}" class="list-group-item list-group-item-action active">Orders</a>
                <a href="{{ url_for('admin.payments') }}" class="list-group-item list-group-item-action">Payments</a>
                <a href="{{ url_for('admin.customers') }}" class="list-group-item list-group-item-action">Customers</a>
            </div>
        </div>
        <div class="col-md-10">
            <h3 class="mb-4">Manage Orders</h3>
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            <div class="card shadow border-0">
                <div class="card-body p-0">
                    <div class="table-responsive">
                        <table class="table table-hover align-middle mb-0">
                            <thead class="table-light">
                                <tr>
                                    <th>Order ID</th>
                                    <th>Customer</th>
                                    <th>Total Amount</th>
                                    <th>Payment Status</th>
                                    <th>Order Status</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for order in orders %}
                                <tr>
                                    <td>{{ order.id }}</td>
                                    <td>{{ order.name }}<br><small class="text-muted">{{ order.email }}</small></td>
                                    <td>₹{{ order.total_amount }}</td>
                                    <td><span class="badge bg-{{ 'success' if order.payment_status == 'PAID' else 'secondary' }}">{{ order.payment_status }}</span></td>
                                    <td>
                                        <form action="{{ url_for('admin.update_order_status', order_id=order.id) }}" method="POST" class="d-flex">
                                            <select name="status" class="form-select form-select-sm me-2" style="width:130px;">
                                                <option value="Pending" {% if order.order_status == 'Pending' %}selected{% endif %}>Pending</option>
                                                <option value="Confirmed" {% if order.order_status == 'Confirmed' %}selected{% endif %}>Confirmed</option>
                                                <option value="Processing" {% if order.order_status == 'Processing' %}selected{% endif %}>Processing</option>
                                                <option value="Shipped" {% if order.order_status == 'Shipped' %}selected{% endif %}>Shipped</option>
                                                <option value="Out for Delivery" {% if order.order_status == 'Out for Delivery' %}selected{% endif %}>Out for Delivery</option>
                                                <option value="Delivered" {% if order.order_status == 'Delivered' %}selected{% endif %}>Delivered</option>
                                                <option value="Cancelled" {% if order.order_status == 'Cancelled' %}selected{% endif %}>Cancelled</option>
                                            </select>
                                            <button type="submit" class="btn btn-sm btn-primary">Update</button>
                                        </form>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''

templates['admin_payments.html'] = '''{% extends 'base.html' %}
{% block title %}Manage Payments - Admin{% endblock %}
{% block content %}
<div class="container-fluid py-4">
    <div class="row">
        <div class="col-md-2 mb-4">
            <div class="list-group shadow-sm border-0">
                <a href="{{ url_for('admin.dashboard') }}" class="list-group-item list-group-item-action">Dashboard</a>
                <a href="{{ url_for('admin.products') }}" class="list-group-item list-group-item-action">Products</a>
                <a href="{{ url_for('admin.inventory') }}" class="list-group-item list-group-item-action">Inventory</a>
                <a href="{{ url_for('admin.orders') }}" class="list-group-item list-group-item-action">Orders</a>
                <a href="{{ url_for('admin.payments') }}" class="list-group-item list-group-item-action active">Payments</a>
                <a href="{{ url_for('admin.customers') }}" class="list-group-item list-group-item-action">Customers</a>
            </div>
        </div>
        <div class="col-md-10">
            <h3 class="mb-4">Payment Records</h3>
            <div class="card shadow border-0">
                <div class="card-body p-0">
                    <div class="table-responsive">
                        <table class="table table-hover align-middle mb-0">
                            <thead class="table-light">
                                <tr>
                                    <th>Order ID</th>
                                    <th>Payment ID</th>
                                    <th>Method</th>
                                    <th>Amount</th>
                                    <th>Status</th>
                                    <th>Date</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for pay in payments %}
                                <tr>
                                    <td>{{ pay.order_id }}</td>
                                    <td><small class="text-muted">{{ pay.razorpay_payment_id }}</small></td>
                                    <td>{{ pay.payment_method }}</td>
                                    <td>₹{{ pay.amount }}</td>
                                    <td><span class="badge bg-success">{{ pay.payment_status }}</span></td>
                                    <td>{{ pay.created_at[:10] }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''

templates['admin_customers.html'] = '''{% extends 'base.html' %}
{% block title %}Customers - Admin{% endblock %}
{% block content %}
<div class="container-fluid py-4">
    <div class="row">
        <div class="col-md-2 mb-4">
            <div class="list-group shadow-sm border-0">
                <a href="{{ url_for('admin.dashboard') }}" class="list-group-item list-group-item-action">Dashboard</a>
                <a href="{{ url_for('admin.products') }}" class="list-group-item list-group-item-action">Products</a>
                <a href="{{ url_for('admin.inventory') }}" class="list-group-item list-group-item-action">Inventory</a>
                <a href="{{ url_for('admin.orders') }}" class="list-group-item list-group-item-action">Orders</a>
                <a href="{{ url_for('admin.payments') }}" class="list-group-item list-group-item-action">Payments</a>
                <a href="{{ url_for('admin.customers') }}" class="list-group-item list-group-item-action active">Customers</a>
            </div>
        </div>
        <div class="col-md-10">
            <h3 class="mb-4">Registered Customers</h3>
            <div class="card shadow border-0">
                <div class="card-body p-0">
                    <div class="table-responsive">
                        <table class="table table-hover align-middle mb-0">
                            <thead class="table-light">
                                <tr>
                                    <th>ID</th>
                                    <th>Name</th>
                                    <th>Email</th>
                                    <th>Mobile</th>
                                    <th>Joined</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for c in customers %}
                                <tr>
                                    <td>{{ c.id }}</td>
                                    <td class="fw-bold">{{ c.name }}</td>
                                    <td>{{ c.email }}</td>
                                    <td>{{ c.mobile }}</td>
                                    <td>{{ c.created_at[:10] }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''

templates['admin_reports.html'] = '''{% extends 'base.html' %}
{% block title %}Reports - Admin{% endblock %}
{% block content %}
<div class="container-fluid py-4">
    <div class="row">
        <div class="col-md-2 mb-4">
            <div class="list-group shadow-sm border-0">
                <a href="{{ url_for('admin.dashboard') }}" class="list-group-item list-group-item-action">Dashboard</a>
                <a href="{{ url_for('admin.products') }}" class="list-group-item list-group-item-action">Products</a>
                <a href="{{ url_for('admin.inventory') }}" class="list-group-item list-group-item-action">Inventory</a>
                <a href="{{ url_for('admin.orders') }}" class="list-group-item list-group-item-action">Orders</a>
                <a href="{{ url_for('admin.payments') }}" class="list-group-item list-group-item-action">Payments</a>
                <a href="{{ url_for('admin.customers') }}" class="list-group-item list-group-item-action">Customers</a>
                <a href="{{ url_for('admin.reports') }}" class="list-group-item list-group-item-action active">Reports</a>
            </div>
        </div>
        <div class="col-md-10">
            <h3 class="mb-4">Reports</h3>
            <div class="alert alert-info">
                Advanced charting and detailed CSV reports will be available in the next release. <br>
                For now, please refer to the main Dashboard for high-level statistics.
            </div>
        </div>
    </div>
</div>
{% endblock %}'''

for name, content in templates.items():
    create_template(name, content)
    print(f"Created {name}")
