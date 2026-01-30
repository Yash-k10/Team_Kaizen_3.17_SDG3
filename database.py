"""Database models and setup for Organ Donation Matching Platform"""
import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import enum
import bcrypt
from math import radians, sin, cos, sqrt, atan2

Base = declarative_base()

# Enums
class UserRole(enum.Enum):
    USER = "user"
    HOSPITAL = "hospital"
    ADMIN = "admin"

class BloodGroup(enum.Enum):
    A_POS = "A+"
    A_NEG = "A-"
    B_POS = "B+"
    B_NEG = "B-"
    AB_POS = "AB+"
    AB_NEG = "AB-"
    O_POS = "O+"
    O_NEG = "O-"

class OrganType(enum.Enum):
    KIDNEY = "kidney"
    LIVER = "liver"
    HEART = "heart"
    LUNG = "lung"
    PANCREAS = "pancreas"
    CORNEA = "cornea"
    INTESTINE = "intestine"
    BONE_MARROW = "bone_marrow"

class ApprovalStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class DonorType(enum.Enum):
    LIVING = "living"
    DECEASED = "deceased"

class UrgencyLevel(enum.Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5

# Models
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    role = Column(Enum(UserRole), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(Text)
    city = Column(String(100), index=True)
    state = Column(String(100), index=True)
    country = Column(String(100), default="India")
    date_of_birth = Column(DateTime)
    age = Column(Integer)
    blood_group = Column(Enum(BloodGroup))
    medical_conditions = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    sos_cases = relationship("SOSCase", back_populates="user", cascade="all, delete-orphan")
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verify password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

class Hospital(Base):
    __tablename__ = 'hospitals'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    hospital_name = Column(String(255), nullable=False, index=True)
    contact_person_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    license_id = Column(String(100), unique=True, nullable=False)
    address = Column(Text, nullable=False)
    city = Column(String(100), index=True)
    state = Column(String(100), index=True)
    country = Column(String(100), default="India")
    latitude = Column(Float)
    longitude = Column(Float)
    capacity = Column(Integer, default=100)
    emergency_contact = Column(String(20))
    approval_status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    donors = relationship("Donor", back_populates="hospital", cascade="all, delete-orphan")
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verify password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

class Donor(Base):
    __tablename__ = 'donors'
    
    id = Column(Integer, primary_key=True)
    hospital_id = Column(Integer, ForeignKey('hospitals.id'), nullable=False)
    donor_type = Column(Enum(DonorType), nullable=False)
    donor_name = Column(String(255))
    age = Column(Integer, nullable=False)
    blood_group = Column(Enum(BloodGroup), nullable=False, index=True)
    organ_type = Column(Enum(OrganType), nullable=False, index=True)
    hla_type = Column(String(100))
    medical_history = Column(Text)
    availability_status = Column(Boolean, default=True, index=True)
    city = Column(String(100), index=True)
    state = Column(String(100), index=True)
    country = Column(String(100), default="India")
    registration_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    approval_status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING)
    reliability_score = Column(Float, default=0.5)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    hospital = relationship("Hospital", back_populates="donors")
    matches = relationship("Match", back_populates="donor", cascade="all, delete-orphan")
    donations = relationship("Donation", back_populates="donor", cascade="all, delete-orphan")

class SOSCase(Base):
    __tablename__ = 'sos_cases'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    patient_name = Column(String(255), nullable=False)
    patient_age = Column(Integer, nullable=False)
    blood_group = Column(Enum(BloodGroup), nullable=False, index=True)
    organ_required = Column(Enum(OrganType), nullable=False, index=True)
    urgency_level = Column(Integer, nullable=False, default=3)
    medical_summary = Column(Text)
    city = Column(String(100), index=True)
    state = Column(String(100), index=True)
    country = Column(String(100), default="India")
    document_path = Column(String(500))
    status = Column(String(50), default="active", index=True)
    approval_status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    resolved_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="sos_cases")
    matches = relationship("Match", back_populates="sos_case", cascade="all, delete-orphan")

class Match(Base):
    __tablename__ = 'matches'
    
    id = Column(Integer, primary_key=True)
    sos_case_id = Column(Integer, ForeignKey('sos_cases.id'))
    donor_id = Column(Integer, ForeignKey('donors.id'), nullable=False)
    compatibility_score = Column(Float, nullable=False, index=True)
    distance_km = Column(Float)
    match_probability = Column(Float, default=0.5)
    urgency_weight = Column(Float, default=1.0)
    final_score = Column(Float, nullable=False, index=True)
    blood_compatible = Column(Boolean, default=False)
    organ_match = Column(Boolean, default=False)
    age_compatible = Column(Boolean, default=False)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    sos_case = relationship("SOSCase", back_populates="matches")
    donor = relationship("Donor", back_populates="matches")

class Donation(Base):
    __tablename__ = 'donations'
    
    id = Column(Integer, primary_key=True)
    donor_id = Column(Integer, ForeignKey('donors.id'), nullable=False)
    recipient_name = Column(String(255), nullable=False)
    organ_type = Column(Enum(OrganType), nullable=False)
    donation_date = Column(DateTime, nullable=False)
    success = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    donor = relationship("Donor", back_populates="donations")

class Admin(Base):
    __tablename__ = 'admins'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    is_super_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    audit_logs = relationship("AuditLog", back_populates="admin", cascade="all, delete-orphan")
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verify password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer, ForeignKey('admins.id'), nullable=False)
    action_type = Column(String(100), nullable=False, index=True)
    target_type = Column(String(50))
    target_id = Column(Integer)
    description = Column(Text, nullable=False)
    ip_address = Column(String(50))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    # Relationships
    admin = relationship("Admin", back_populates="audit_logs")

# Database setup
class DatabaseManager:
    def __init__(self, db_path="data/organ_donation.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def get_session(self):
        """Get database session"""
        return self.Session()
    
    def init_admin(self):
        """Initialize admin user from environment variable"""
        session = self.get_session()
        try:
            admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
            admin_password = os.environ.get('ADMIN_PASSWORD', 'Admin@123')
            admin_email = os.environ.get('ADMIN_EMAIL', 'admin@jeevSetu.com')
            
            existing_admin = session.query(Admin).filter_by(username=admin_username).first()
            if not existing_admin:
                admin = Admin(
                    username=admin_username,
                    email=admin_email,
                    full_name="System Administrator",
                    is_super_admin=True
                )
                admin.set_password(admin_password)
                session.add(admin)
                session.commit()
                print(f"✅ Admin user created: {admin_username}")
            else:
                print(f"✅ Admin user already exists: {admin_username}")
        except Exception as e:
            session.rollback()
            print(f"❌ Error creating admin: {str(e)}")
        finally:
            session.close()

# Utility functions
def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    if None in [lat1, lon1, lat2, lon2]:
        return None
    
    R = 6371  # Earth's radius in kilometers
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    
    return distance

def get_blood_compatible_groups(blood_group):
    """Get list of compatible blood groups for donation"""
    compatibility = {
        BloodGroup.O_NEG: [BloodGroup.O_NEG, BloodGroup.O_POS, BloodGroup.A_NEG, BloodGroup.A_POS, 
                           BloodGroup.B_NEG, BloodGroup.B_POS, BloodGroup.AB_NEG, BloodGroup.AB_POS],
        BloodGroup.O_POS: [BloodGroup.O_POS, BloodGroup.A_POS, BloodGroup.B_POS, BloodGroup.AB_POS],
        BloodGroup.A_NEG: [BloodGroup.A_NEG, BloodGroup.A_POS, BloodGroup.AB_NEG, BloodGroup.AB_POS],
        BloodGroup.A_POS: [BloodGroup.A_POS, BloodGroup.AB_POS],
        BloodGroup.B_NEG: [BloodGroup.B_NEG, BloodGroup.B_POS, BloodGroup.AB_NEG, BloodGroup.AB_POS],
        BloodGroup.B_POS: [BloodGroup.B_POS, BloodGroup.AB_POS],
        BloodGroup.AB_NEG: [BloodGroup.AB_NEG, BloodGroup.AB_POS],
        BloodGroup.AB_POS: [BloodGroup.AB_POS]
    }
    return compatibility.get(blood_group, [])

if __name__ == "__main__":
    db_manager = DatabaseManager()
    db_manager.init_admin()
    print("✅ Database initialized successfully!")
