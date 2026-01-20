# E-Commerce API - Restructured

A well-organized FastAPI e-commerce platform with clean architecture and separation of concerns.

## 📁 Project Structure

```
app/
├── main.py                     # Application entry point
│
├── core/                       # Core configuration
│   ├── __init__.py
│   ├── config.py              # Settings and configuration
│   └── constants.py           # Application constants
│
├── database/                   # Database configuration
│   ├── __init__.py
│   ├── base.py               # SQLAlchemy Base
│   └── db.py                 # Engine and session
│
├── models/                     # SQLAlchemy models
│   ├── __init__.py
│   ├── user.py
│   ├── product.py
│   ├── cart.py
│   ├── order.py
│   ├── order_item.py
│   ├── inventory.py
│   └── payment.py
│
├── schemas/                    # Pydantic schemas
│   ├── __init__.py
│   ├── user.py
│   ├── product.py
│   ├── cart.py
│   ├── inventory.py
│   ├── order.py
│   └── payment.py
│
├── dependencies/               # FastAPI dependencies
│   ├── __init__.py
│   ├── db.py                 # Database session
│   └── auth.py               # Authentication & authorization
│
├── services/                   # Business logic
│   ├── __init__.py
│   ├── inventory_service.py
│   ├── order_service.py
│   └── payment_service.py
│
└── routers/                    # API routes
    ├── __init__.py
    ├── auth.py               # Authentication endpoints
    ├── product.py            # Product endpoints
    ├── cart.py               # Cart endpoints
    ├── order.py              # Order endpoints
    ├── payment.py            # Payment endpoints
    ├── inventory.py          # Inventory endpoints
    └── admin.py              # Admin/seller endpoints
```

## 🏗️ Architecture

### Layers

1. **Routers Layer** (`routers/`)
   - HTTP request/response handling
   - Input validation
   - Route definitions
   - Error handling

2. **Services Layer** (`services/`)
   - Business logic
   - Transaction management
   - Complex operations
   - Cross-model operations

3. **Models Layer** (`models/`)
   - Database schema
   - SQLAlchemy ORM models
   - Relationships

4. **Schemas Layer** (`schemas/`)
   - Request/response validation
   - Pydantic models
   - Data serialization

5. **Dependencies Layer** (`dependencies/`)
   - Reusable dependencies
   - Authentication
   - Database sessions

6. **Core Layer** (`core/`)
   - Configuration
   - Constants
   - Settings

## 🚀 Installation

### Prerequisites

- Python 3.8+
- MySQL 8.0+
- pip

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ecommerce-api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Create database**
   ```bash
   mysql -u root -p
   CREATE DATABASE ecommerce_db;
   ```

6. **Run the application**
   ```bash
   python main.py
   ```

   Or with uvicorn:
   ```bash
   uvicorn main:app --reload
   ```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔑 Default Credentials

- **Username**: admin
- **Password**: admin123
- **Role**: seller

## 📋 API Endpoints

### Authentication
- `POST /register` - Register new buyer
- `POST /login` - Login and get token

### Products
- `GET /products` - List all products
- `GET /products/{id}` - Get product details
- `POST /products` - Create product (seller)
- `PUT /products/{id}` - Update product (seller)
- `DELETE /products/{id}` - Delete product (seller)

### Cart
- `GET /cart` - View cart (buyer)
- `POST /cart` - Add to cart (buyer)
- `PUT /cart/{id}` - Update cart item (buyer)
- `DELETE /cart/{id}` - Remove from cart (buyer)

### Orders
- `GET /orders` - List my orders (buyer)
- `GET /orders/{id}` - Get order details (buyer)
- `POST /orders` - Place order (buyer)
- `POST /orders/{id}/cancel` - Cancel order (buyer)

### Payments
- `POST /payments/orders/{id}/pay` - Process payment (buyer)
- `GET /payments/orders/{id}/payments` - Payment history (buyer)

### Inventory
- `GET /inventory` - List inventory (seller)
- `GET /inventory/{product_id}` - Get inventory (seller)
- `POST /inventory` - Create inventory (seller)
- `PUT /inventory/{product_id}` - Update inventory (seller)

### Admin
- `GET /admin/orders` - List all orders (seller)
- `POST /admin/orders/{id}/ship` - Ship order (seller)
- `POST /admin/orders/{id}/deliver` - Deliver order (seller)
- `POST /admin/orders/{id}/refund` - Refund order (seller)

## 🎯 Key Features

### Clean Architecture
- Clear separation of concerns
- Each layer has a single responsibility
- Easy to test and maintain

### Modular Design
- Each feature in its own module
- Easy to add new features
- Reusable components

### Type Safety
- Full type hints throughout
- Pydantic validation
- SQLAlchemy models with types

### Error Handling
- Custom exceptions
- Proper HTTP status codes
- Transaction rollback

### Security
- JWT authentication
- Role-based access control
- Password hashing (bcrypt)

### Database
- Row-level locking
- Transaction management
- Relationship handling

## 🧪 Testing

```bash
pytest
```

## 📝 Configuration

All configuration is managed through environment variables (see `.env.example`).

Key settings:
- Database connection
- JWT secret and expiration
- CORS origins
- Logging level

## 🔄 Adding New Features

### 1. Add a Model

Create `app/models/new_model.py`:
```python
from sqlalchemy import Column, Integer, String
from app.database.base import Base

class NewModel(Base):
    __tablename__ = "new_models"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
```

### 2. Add Schemas

Create `app/schemas/new_model.py`:
```python
from pydantic import BaseModel

class NewModelCreate(BaseModel):
    name: str

class NewModelOut(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True
```

### 3. Add Service (if needed)

Create `app/services/new_service.py` for business logic.

### 4. Add Router

Create `app/routers/new_router.py`:
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas import NewModelCreate, NewModelOut

router = APIRouter(prefix="/new", tags=["New Feature"])

@router.post("", response_model=NewModelOut)
def create_new(item: NewModelCreate, db: Session = Depends(get_db)):
    # Implementation
    pass
```

### 5. Register Router

In `main.py`:
```python
from app.routers import new_router
app.include_router(new_router.router)
```

## 🛠️ Development Guidelines

### Code Organization
- Keep routers thin - delegate to services
- Put business logic in services
- Use dependencies for reusable logic
- Keep models focused on database schema

### Naming Conventions
- Models: Singular (User, Product)
- Tables: Plural (users, products)
- Services: *_service.py
- Routers: Feature name (auth.py, product.py)

### Error Handling
- Use custom exceptions in services
- Convert to HTTPException in routers
- Always rollback on errors
- Log important operations

## 📄 License

MIT License

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For issues and questions, please open an issue on GitHub.