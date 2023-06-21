from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, UUID, DateTime
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import os

Base = declarative_base()


# Define the User and Upload classes as ORM models:
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String)
    uploads = relationship("Upload", back_populates="user")


class Upload(Base):
    __tablename__ = 'uploads'

    id = Column(Integer, primary_key=True)
    uid = Column(UUID(as_uuid=True), unique=True, nullable=False)
    filename = Column(String)
    upload_time = Column(DateTime)
    finish_time = Column(DateTime)
    status = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="uploads")


# Create a database engine and session:
database_path = os.path.join('db', 'database.db')
engine = create_engine(f'sqlite:///{database_path}')
Session = sessionmaker(bind=engine)
session = Session()

# Create the database tables if they don't exist:
Base.metadata.create_all(engine)
