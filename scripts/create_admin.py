import asyncio
from app.models.user import User
from app.core.database import SessionLocal
from app.services.auth_service import AuthService

async def create_admin():
    db = SessionLocal()
    auth_service = AuthService()
    try:
        await auth_service.create_user(
            db=db,
            username='admin',
            email='admin@example.com',
            password='admin',
            full_name='Admin User',
            role='ADMIN'
        )
        print("Admin user created successfully")
    except Exception as e:
        print(f"Error creating admin user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(create_admin()) 