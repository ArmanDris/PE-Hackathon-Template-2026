# MLH PE Hackathon — Flask + Peewee + PostgreSQL Template

A minimal hackathon starter template. You get the scaffolding and database wiring — you build the models, routes, and CSV loading logic.

**Stack:** Flask · Peewee ORM · PostgreSQL · uv

## **Important**

Our project was based on seed files provided by [MLH PE Hackathon (https://mlh-pe-hackathon.com) platform. It was the basis for the schema of the database, and provided some intial data.

## Prerequisites

- **uv** — a fast Python package manager that handles Python versions, virtual environments, and dependencies automatically.
  Install it with:

  ```bash
  # macOS / Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh

  # Windows (PowerShell)
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

  For other methods see the [uv installation docs](https://docs.astral.sh/uv/getting-started/installation/).

- PostgreSQL running locally (you can use Docker or a local instance)

## uv Basics

`uv` manages your Python version, virtual environment, and dependencies automatically — no manual `python -m venv` needed.

| Command               | What it does                                             |
| --------------------- | -------------------------------------------------------- |
| `uv sync`             | Install all dependencies (creates `.venv` automatically) |
| `uv run <script>`     | Run a script using the project's virtual environment     |
| `uv add <package>`    | Add a new dependency                                     |
| `uv remove <package>` | Remove a dependency                                      |

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/ArmanDris/PE-Hackathon-Template-2026.git && cd PE-Hackathon-Template-2026.git

# 2. Install dependencies
uv sync

# 3. Create the database(**As postgres user*)
createdb hackathon_db

# 4. Configure environment
cp .env.example .env   # edit if your DB credentials differ

# 5. Run the server
uv run run.py

# 6. Verify
curl http://localhost:5000/health
# → {"status":"ok"}
```

## Run With Docker Compose

```bash
# 1. Create env file (if you do not already have one)
cp .env.example .env

# 2. Build and start multiple instances of web
`docker compose up --build --scale web=3`

# 3. Verify
curl http://localhost:5000/health
# → {"status":"ok"}
```

The production stack uses Nginx as a simple load balancer in front of multiple `web` containers.
Change `--scale web=3` to any number you want.

For development, use the dev override so only one `web` container runs and it is published directly:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

Useful commands:

```bash
# Stop services
docker compose down

# Stop services and remove Postgres data volume
docker compose down -v

```

## Run Tests with Docker

```bash
# Start services if not done already
docker compose up -d

# Run tests
docker compose exec web uv run pytest -v
```

## Project Structure

```
mlh-pe-hackathon/
├── app/
│   ├── __init__.py          # App factory (create_app)
│   ├── database.py          # DatabaseProxy, BaseModel, connection hooks
│   ├── models/
│   │   └── __init__.py      # Import your models here
│   └── routes/
│   |   └── __init__.py      # register_routes() — add blueprints here
|   └── templates            # Add any html files to render_template(index.html)
|   └── statc                # Css/JavaScript files
|   └── logging
|       └── logs             # Path for app.log
|       └── auth             # Where credential hashes are stored(ONLY FOR TESTING)
|       └── filter           # Add any custom filters for python.logging
├── .env.example             # DB connection template
├── .gitignore               # Python + uv gitignore
├── .python-version          # Pin Python version for uv
├── pyproject.toml           # Project metadata + dependencies
├── run.py                   # Entry point: uv run run.py
└── README.md
```

## How to Add a Model
This will guide you through adding the 'product' model, this process should be repeated for any models you wish to use in your app

1. Create a file in `app/models/`, e.g. `app/models/product.py`:

```python
from peewee import CharField, DecimalField, IntegerField

from app.database import BaseModel


class Product(BaseModel):
    name = CharField()
    category = CharField()
    price = DecimalField(decimal_places=2)
    stock = IntegerField()
```

2. Import it in `app/models/__init__.py`:

```python
from app.models.product import Product
```

3. Create the table (run once in a Python shell or a setup script):

```python
from app.database import db
from app.models.product import Product

db.create_tables([Product])
```

## How to Add Routes

1. Create a blueprint in `app/routes/`, e.g. `app/routes/products.py`:

```python
from flask import Blueprint, jsonify
from playhouse.shortcuts import model_to_dict

from app.models.product import Product

products_bp = Blueprint("products", __name__)


@products_bp.route("/products")
def list_products():
    products = Product.select()
    return jsonify([model_to_dict(p) for p in products])
```

2. Register it in `app/routes/__init__.py`:

```python
def register_routes(app):
    from app.routes.products import products_bp
    app.register_blueprint(products_bp)
```

## How to Load CSV Data

```python
import csv
from peewee import chunked
from app.database import db
from app.models.product import Product

def load_csv(filepath):
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    with db.atomic():
        for batch in chunked(rows, 100):
            Product.insert_many(batch).execute()
            # *IMPORTANT* This will save any nested json as a string
```

## Useful Peewee Patterns

```python
from peewee import fn
from playhouse.shortcuts import model_to_dict

# Select all
products = Product.select()

# Filter
cheap = Product.select().where(Product.price < 10)

# Get by ID
p = Product.get_by_id(1)

# Create
Product.create(name="Widget", category="Tools", price=9.99, stock=50)

# Convert to dict (great for JSON responses)
model_to_dict(p)

# Aggregations
avg_price = Product.select(fn.AVG(Product.price)).scalar()
total = Product.select(fn.SUM(Product.stock)).scalar()

# Group by
from peewee import fn
query = (Product
         .select(Product.category, fn.COUNT(Product.id).alias("count"))
         .group_by(Product.category))
```

## Tips

- Use `model_to_dict` from `playhouse.shortcuts` to convert model instances to dictionaries for JSON responses.
- Wrap bulk inserts in `db.atomic()` for transactional safety and performance.
- The template uses `teardown_appcontext` for connection cleanup, so connections are closed even when requests fail.
- Check `.env.example` for all available configuration options.
