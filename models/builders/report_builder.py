from models.report import Report


class ReportBuilder:
    def __init__(self):
        self._user_id     = None
        self._description = None
        self._latitude    = None
        self._longitude   = None
        self._severity    = None
        self._status      = "pending"
        self._image_url_1 = None
        self._image_url_2 = None
        self._image_url_3 = None
        self._ai_note     = None

    def set_user(self, user_id: int):
        self._user_id = user_id
        return self

    def set_description(self, description: str):
        self._description = description.strip()
        return self

    def set_location(self, latitude: float, longitude: float):
        self._latitude  = float(latitude)
        self._longitude = float(longitude)
        return self

    def set_images(self, url1=None, url2=None, url3=None):
        self._image_url_1 = url1
        self._image_url_2 = url2
        self._image_url_3 = url3
        return self

    def set_ai_result(self, severity: str, ai_note: str):
        if severity not in ("low", "medium", "high", None):
            raise ValueError(f"Invalid severity: {severity}")
        self._severity = severity
        self._ai_note  = ai_note
        return self

    def set_status(self, status: str):
        if status not in Report.STATUSES:
            raise ValueError(f"Invalid status: {status}")
        self._status = status
        return self

    def build(self) -> Report:
        if not all([self._user_id, self._description,
                    self._latitude is not None,
                    self._longitude is not None]):
            raise ValueError("user_id, description, latitude, longitude are required.")
        return Report(
            user_id     = self._user_id,
            description = self._description,
            latitude    = self._latitude,
            longitude   = self._longitude,
            severity    = self._severity,
            status      = self._status,
            image_url_1 = self._image_url_1,
            image_url_2 = self._image_url_2,
            image_url_3 = self._image_url_3,
            ai_note     = self._ai_note,
        )