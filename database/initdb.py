from database.database import engine
from models.user import Base
from models.ecg import ECGDatabase

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Done.")
