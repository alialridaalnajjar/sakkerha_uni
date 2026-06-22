from database import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(db.Model):
    __tablename__ = "users"

    id          = db.Column(db.Integer,     primary_key=True)
    first_name  = db.Column(db.String(80),  nullable=False)
    last_name   = db.Column(db.String(80),  nullable=False)
    email       = db.Column(db.String(120), nullable=False, unique=True)
    password    = db.Column(db.String(256), nullable=False)
    role        = db.Column(db.String(10),  nullable=False, default="user")
    bio         = db.Column(db.Text,        nullable=True)
    dob         = db.Column(db.Date,        nullable=True)
    image_pfp   = db.Column(db.String(500), nullable=True)
    username    = db.Column(db.String(80),  nullable=True)
    created_at  = db.Column(db.DateTime,    default=datetime.utcnow)

    # Relationship to reports
    reports     = db.relationship("Report", back_populates="user",
                                  cascade="all, delete-orphan", lazy="dynamic")

    # ── Computed properties ───────────────────────────────
    @property
    def initials(self):
        return f"{self.first_name[0]}{self.last_name[0]}".upper()

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    # ── Password ──────────────────────────────────────────
    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def verify_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    # ── Queries ───────────────────────────────────────────
    @classmethod
    def find_by_id(cls, user_id):
        return db.session.get(cls, user_id)

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username.strip()).first()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email.lower().strip()).first()
    @classmethod
    def update_profile(cls, user_id, bio, dob):
        user = db.session.get(cls, user_id)
        if user:
            user.bio = bio
            user.dob = dob
            db.session.commit()

    @classmethod
    def update_pfp(cls, user_id, pfp_url):
        user = db.session.get(cls, user_id)
        if user:
            user.image_pfp = pfp_url
            db.session.commit()

    @classmethod
    def delete_account(cls, user_id):
        user = db.session.get(cls, user_id)
        if user:
            db.session.delete(user)  # cascades to reports via relationship
            db.session.commit()
            return True
        return False

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __repr__(self):
        return f"<User {self.email}>"