from app.routes.users import users_bp
from app.routes.products import products_bp

def register_routes(app):
    """Register all route blueprints with the Flask app."""
    app.register_blueprint(products_bp)
    app.register_blueprint(users_bp)
