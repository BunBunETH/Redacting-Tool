from sqlalchemy import Column, String, Boolean, Enum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    REVIEWER = "reviewer"
    VIEWER = "viewer"

class User(BaseModel):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(Enum(UserRole), default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True)
    api_key = Column(String, unique=True, index=True)
    
    # Relationships
    feedback = relationship("VaultFeedback", back_populates="reviewer")

    def has_permission(self, permission: str) -> bool:
        """
        Check if user has a specific permission based on their role.
        Permissions are mapped to roles as follows:
        - ADMIN: all permissions
        - REVIEWER: vault:read, vault:feedback
        - VIEWER: vault:read
        """
        if not self.is_active:
            return False

        if self.role == UserRole.ADMIN:
            return True

        role_permissions = {
            UserRole.REVIEWER: ["vault:read", "vault:feedback"],
            UserRole.VIEWER: ["vault:read"]
        }

        return permission in role_permissions.get(self.role, []) 