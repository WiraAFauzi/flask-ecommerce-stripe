import os
import stripe
from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from models import db, User, Product, Order
from api import api
from webhook import webhook

load_dotenv()

app = Flask(__name__)
app.config.from_object("config.Config")

# ---------- UPLOAD CONFIG ----------
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


db.init_app(app)

# ---------- LOGIN ----------
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ---------- STRIPE ----------
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


# ---------- BLUEPRINTS ----------
app.register_blueprint(api)
app.register_blueprint(webhook)


# ---------- STORE ----------

@app.route("/")
def store():
    products = Product.query.all()
    return render_template("store.html", products=products)


@app.route("/product/<int:product_id>")
def product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("product.html", product=product)


# ---------- AUTH ----------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password_hash = generate_password_hash(request.form["password"])

        if User.query.filter_by(email=email).first():
            flash("Email already registered", "danger")
            return redirect("/register")

        user = User(email=email, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect("/")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()

        if user and check_password_hash(
            user.password_hash, request.form["password"]
        ):
            login_user(user)
            return redirect("/")

        flash("Invalid email or password", "danger")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


# ---------- ORDERS ----------

@app.route("/orders", methods=["GET", "POST"])
@login_required
def orders():
    if request.method == "POST":
        product = Product.query.get_or_404(request.form["product_id"])
        quantity = int(request.form["quantity"])

        order = Order(
            user_email=current_user.email,
            product_name=product.name,
            price=product.price,
            quantity=quantity,
            total=product.price * quantity,
            status="pending",
        )

        db.session.add(order)
        db.session.commit()
        return redirect("/orders")

    orders = Order.query.filter_by(user_email=current_user.email).all()
    return render_template("orders.html", orders=orders)


# ---------- CHECKOUT ----------

@app.route("/checkout/<int:order_id>")
@login_required
def checkout(order_id):
    order = Order.query.get_or_404(order_id)

    if order.user_email != current_user.email:
        abort(403)

    if order.status != "pending":
        flash("Order already paid", "warning")
        return redirect("/orders")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        client_reference_id=str(order.id),
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": order.product_name},
                "unit_amount": int(order.price * 100),
            },
            "quantity": order.quantity,
        }],
        customer_email=current_user.email,
        success_url=url_for("success", _external=True),
        cancel_url=url_for("orders", _external=True),
    )

    return redirect(session.url)


@app.route("/success")
@login_required
def success():
    return render_template("success.html")


# ---------- ADMIN ----------

@app.route("/admin")
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect("/")

    return render_template(
        "admin/dashboard.html",
        products_count=Product.query.count(),
        orders_count=Order.query.count(),
    )


@app.route("/admin/orders")
@login_required
def admin_orders():
    if not current_user.is_admin:
        return redirect("/")

    orders = Order.query.all()
    return render_template("admin/orders.html", orders=orders)


@app.route("/admin/orders/ship/<int:order_id>", methods=["POST"])
@login_required
def ship_order(order_id):
    if not current_user.is_admin:
        abort(403)

    order = Order.query.get_or_404(order_id)

    if order.status != "paid":
        flash("Only paid orders can be shipped", "warning")
        return redirect("/admin/orders")

    order.status = "shipped"
    db.session.commit()

    flash(f"Order #{order.id} marked as shipped", "success")
    return redirect("/admin/orders")


# ---------- ADMIN PRODUCTS (WITH IMAGE UPLOAD) ----------

@app.route("/admin/products", methods=["GET", "POST"])
@login_required
def admin_products():
    if not current_user.is_admin:
        return redirect("/")

    if request.method == "POST":
        file = request.files.get("image")
        filename = None

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        product = Product(
            name=request.form["name"],
            description=request.form["description"],
            price=float(request.form["price"]),
            image=filename or "default.jpg",
        )

        db.session.add(product)
        db.session.commit()
        return redirect("/admin/products")

    products = Product.query.all()
    return render_template("admin/products.html", products=products)


@app.route("/admin/products/edit/<int:product_id>", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    if not current_user.is_admin:
        return redirect("/")

    product = Product.query.get_or_404(product_id)

    if request.method == "POST":
        product.name = request.form["name"]
        product.description = request.form["description"]
        product.price = float(request.form["price"])

        file = request.files.get("image")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            product.image = filename

        db.session.commit()
        return redirect("/admin/products")

    return render_template("admin/edit_product.html", product=product)


@app.route("/admin/delete-product/<int:product_id>")
@login_required
def delete_product(product_id):
    if not current_user.is_admin:
        return redirect("/")

    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect("/admin/products")


# ---------- RUN ----------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
