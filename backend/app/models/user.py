from sqlalchemy import Column, Integer, String, SmallInteger, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Group(Base):
    __tablename__ = "tb_groups"

    id_row = Column(Integer, primary_key=True, autoincrement=True)
    id_group = Column(String(10), unique=True, nullable=False)
    name_group = Column(String(50), nullable=False)
    level_group = Column(SmallInteger, nullable=False)
    create_date = Column(DateTime, server_default=func.current_timestamp(), nullable=False)

    # Relationships
    users = relationship("User", back_populates="group")


class UserStatus(Base):
    __tablename__ = "tb_user_status"

    id_row = Column(Integer, primary_key=True, autoincrement=True)
    status_user = Column(String(3), unique=True, nullable=False)
    description_status = Column(String(50), nullable=False)
    create_date = Column(DateTime, server_default=func.current_timestamp(), nullable=False)

    # Relationships
    users = relationship("User", back_populates="status")


class User(Base):
    __tablename__ = "tb_users"

    id_row = Column(Integer, primary_key=True, autoincrement=True)
    id_user = Column(String(10), unique=True, nullable=False)
    name_user = Column(String(50), nullable=False)
    mail_user = Column(String(50), nullable=False)
    id_group = Column(String(10), ForeignKey("tb_groups.id_group"), nullable=False)
    status_user = Column(String(3), ForeignKey("tb_user_status.status_user"), nullable=False)
    pass_user = Column(String(255), nullable=False)  # Increased for hashed passwords
    create_date = Column(DateTime, server_default=func.current_timestamp(), nullable=False)

    # Relationships
    group = relationship("Group", back_populates="users")
    status = relationship("UserStatus", back_populates="users")
    items = relationship("Item", back_populates="user")
