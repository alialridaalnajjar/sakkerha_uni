from database import db
from datetime import datetime


class Report(db.Model):
    __tablename__ = "reports"

    id          = db.Column(db.Integer,       primary_key=True)
    user_id     = db.Column(db.Integer,       db.ForeignKey("users.id"), nullable=False)
    description = db.Column(db.Text,          nullable=False)
    latitude    = db.Column(db.Numeric(10,7), nullable=False)
    longitude   = db.Column(db.Numeric(10,7), nullable=False)
    severity    = db.Column(db.String(10),    nullable=True)   # low | medium | high
    status      = db.Column(db.String(10),    nullable=False, default="pending")
    image_url_1 = db.Column(db.Text,          nullable=True)
    image_url_2 = db.Column(db.Text,          nullable=True)
    image_url_3 = db.Column(db.Text,          nullable=True)
    ai_note     = db.Column(db.Text,          nullable=True)
    title       = db.Column(db.String(200),   nullable=True)
    created_at  = db.Column(db.DateTime,      default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime,      default=datetime.utcnow,
                                              onupdate=datetime.utcnow)

    STATUSES   = ("pending", "ongoing", "completed", "rejected", "invalid")
    SEVERITIES = ("low", "medium", "high", "invalid")

    # Relationship back to user
    user = db.relationship("User", back_populates="reports")

    # ── Computed properties ───────────────────────────────
    @property
    def images(self):
        return [u for u in [self.image_url_1, self.image_url_2, self.image_url_3] if u]

    @property
    def reporter_name(self):
        if self.user:
            return self.user.full_name
        return "Unknown"

    @property
    def user_email(self):
        return self.user.email if self.user else "—"

    # ── Queries ───────────────────────────────────────────
    @classmethod
    def find_by_id(cls, report_id):
        return db.session.get(cls, report_id)

    @classmethod
    def find_by_user(cls, user_id):
        return (cls.query
                .filter_by(user_id=user_id)
                .order_by(cls.created_at.desc())
                .all())

    @classmethod
    def find_public(cls):
        return (cls.query
                .filter(cls.status.in_(["ongoing", "completed"]))
                .order_by(cls.created_at.desc())
                .all())

    @classmethod
    def find_all(cls, status=None, severity=None, search=None, exclude_invalid=False):
        from models.user import User
        q = cls.query.join(User)
        if status:
            q = q.filter(cls.status == status)
        elif exclude_invalid:
            q = q.filter(cls.status != "invalid")
        if severity:
            q = q.filter(cls.severity == severity)
        if search:
            q = q.filter(
                db.or_(
                    cls.description.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%")
                )
            )
        return q.order_by(cls.created_at.desc()).all()

    # ── Mutations ─────────────────────────────────────────
    @classmethod
    def update_status(cls, report_id, new_status):
        report = db.session.get(cls, report_id)
        if report:
            report.status     = new_status
            report.updated_at = datetime.utcnow()
            db.session.commit()

    @classmethod
    def delete(cls, report_id):
        report = db.session.get(cls, report_id)
        if report:
            db.session.delete(report)
            db.session.commit()
            return True
        return False

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __repr__(self):
        return f"<Report #{self.id} {self.status}>"