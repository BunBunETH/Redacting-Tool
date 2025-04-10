from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.core.config import settings
import secrets
import logging

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self):
        self.secret_key = settings.JWT_SECRET
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False

    def get_password_hash(self, password: str) -> str:
        try:
            return pwd_context.hash(password)
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        try:
            to_encode = data.copy()
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(minutes=15)
            to_encode.update({"exp": expire})
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            raise

    def verify_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.error(f"Error verifying token: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error verifying token: {e}")
            return None

    async def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        try:
            user = db.query(User).filter(User.username == username).first()
            if not user:
                logger.warning(f"Authentication failed: User {username} not found")
                return None
            if not self.verify_password(password, user.hashed_password):
                logger.warning(f"Authentication failed: Invalid password for user {username}")
                return None
            return user
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None

    async def create_user(
        self,
        db: Session,
        username: str,
        email: str,
        password: str,
        full_name: str,
        role: UserRole = UserRole.VIEWER
    ) -> User:
        try:
            hashed_password = self.get_password_hash(password)
            api_key = secrets.token_urlsafe(32)
            
            user = User(
                username=username,
                email=email,
                hashed_password=hashed_password,
                full_name=full_name,
                role=role,
                api_key=api_key
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"User {username} created successfully")
            return user
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            db.rollback()
            raise

    async def get_current_user(self, db: Session, token: str) -> Optional[User]:
        try:
            payload = self.verify_token(token)
            if payload is None:
                return None
            username: str = payload.get("sub")
            if username is None:
                return None
            return db.query(User).filter(User.username == username).first()
        except Exception as e:
            logger.error(f"Error getting current user: {e}")
            return None

    async def get_user_by_api_key(self, db: Session, api_key: str) -> Optional[User]:
        try:
            return db.query(User).filter(User.api_key == api_key).first()
        except Exception as e:
            logger.error(f"Error getting user by API key: {e}")
            return None

    def has_permission(self, user: User, required_role: UserRole) -> bool:
        try:
            role_hierarchy = {
                UserRole.ADMIN: 3,
                UserRole.REVIEWER: 2,
                UserRole.VIEWER: 1
            }
            return role_hierarchy[user.role] >= role_hierarchy[required_role]
        except Exception as e:
            logger.error(f"Error checking permissions: {e}")
            return False 