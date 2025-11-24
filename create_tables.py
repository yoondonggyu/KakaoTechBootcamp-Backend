from app.core.database import engine, Base
from app.models import user, post, comment

# Create all tables
print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")
