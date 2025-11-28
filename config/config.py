from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Reemplaza con tu información de conexión de RDS
DATABASE_URL = "postgresql://username:password@your-rds-endpoint:port/dbname"

# Para MySQL usa: mysql+pymysql://username:password@your-rds-endpoint:port/dbname

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
