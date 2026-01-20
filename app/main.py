"""
FastAPI E-Commerce Application
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.core.constants import ROLE_SELLER
from app.database import Base, engine, SessionLocal
from app.models import User
from app.dependencies import hash_password
from app.routers import auth, product, cart, order, payment, inventory, admin

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A comprehensive e-commerce platform API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------
# Startup Events
# -------------------------------------------------
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")

    # Create default seller account
    db = SessionLocal()
    try:
        admin = db.query(User).filter(
            User.username == "admin"
        ).first()

        if not admin:
            admin = User(
                username="admin",
                email="admin@ecommerce.com",
                password=hash_password("admin123"),
                role=ROLE_SELLER
            )
            db.add(admin)
            db.commit()
            logger.info("Default admin user created")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        db.rollback()
    finally:
        db.close()


# -------------------------------------------------
# Health Check
# -------------------------------------------------
@app.get("/health", tags=["Health"])
def health_check():
    """Check API health status"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "app": settings.APP_NAME
    }


# -------------------------------------------------
# Include Routers
# -------------------------------------------------
app.include_router(auth.router)
app.include_router(product.router)
app.include_router(inventory.router)
app.include_router(cart.router)
app.include_router(order.router)
app.include_router(payment.router)
app.include_router(admin.router)


# -------------------------------------------------
# Root Endpoint
# -------------------------------------------------
@app.get("/", tags=["Root"])
def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )