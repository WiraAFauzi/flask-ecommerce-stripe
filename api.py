from flask import Blueprint, jsonify, request
from models import Product

api = Blueprint("api", __name__, url_prefix="/api")

@api.route("/products")
def get_products():
    products = Product.query.all()
    return jsonify([
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "description": p.description,
            "image": p.image
        } for p in products
    ])

@api.route("/product/<int:product_id>")
def get_product(product_id):
    p = Product.query.get_or_404(product_id)
    return jsonify({
        "id": p.id,
        "name": p.name,
        "price": p.price,
        "description": p.description,
        "image": p.image
    })
