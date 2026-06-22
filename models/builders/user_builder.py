from models.user import User


class UserBuilder:
    def __init__(self):
        self._first_name = None
        self._last_name  = None
        self._username   = None
        self._email      = None
        self._password   = None
        self._role       = "user"
        self._bio        = None
        self._dob        = None
        self._image_pfp  = None

    def set_name(self, first_name: str, last_name: str):
        self._first_name = first_name.strip()
        self._last_name  = last_name.strip()
        return self

    def set_username(self, username: str):
        self._username = username.strip()
        return self

    def set_email(self, email: str):
        self._email = email.strip().lower()
        return self

    def set_password(self, password: str):
        self._password = password
        return self

    def set_role(self, role: str):
        if role not in ("user", "admin"):
            raise ValueError(f"Invalid role: {role}")
        self._role = role
        return self

    def set_bio(self, bio: str):
        self._bio = bio
        return self

    def set_dob(self, dob):
        self._dob = dob
        return self

    def set_image_pfp(self, image_pfp: str):
        self._image_pfp = image_pfp
        return self

    def build(self) -> User:
        if not all([self._first_name, self._last_name, self._email, self._password]):
            raise ValueError("first_name, last_name, email and password are required.")
        user = User(
            first_name = self._first_name,
            last_name  = self._last_name,
            username   = self._username,
            email      = self._email,
            role       = self._role,
            bio        = self._bio,
            dob        = self._dob,
            image_pfp  = self._image_pfp,
        )
        user.set_password(self._password)  # uses werkzeug hash via model method
        return user