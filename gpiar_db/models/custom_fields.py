import json
from peewee import TextField, CharField


class JSONField(TextField):
    """
    A field that stores a JSON object as a string in the database.
    """

    def db_value(self, value):
        if value is None:
            return value
        return json.dumps(value)

    def python_value(self, value):
        if value is None:
            return value
        return json.loads(value)


class PointField(JSONField):
    """
    A JSON field that validates a single point:
    must be a dict with keys 'lat' and 'lon' that are floats.
    """

    def python_value(self, value):
        data = super().python_value(value)
        if data is None:
            return data
        if not isinstance(data, dict) or 'lat' not in data or 'lon' not in data:
            raise ValueError(
                "PointField expects a dict with 'lat' and 'lon' keys")
        try:
            data['lat'] = float(data['lat'])
            data['lon'] = float(data['lon'])
        except (TypeError, ValueError):
            raise ValueError("lat and lon must be float values")
        return data

    def db_value(self, value):
        if value is None:
            return value
        if not isinstance(value, dict) or 'lat' not in value or 'lon' not in value:
            raise ValueError(
                "PointField expects a dict with 'lat' and 'lon' keys")
        try:
            value['lat'] = float(value['lat'])
            value['lon'] = float(value['lon'])
        except (TypeError, ValueError):
            raise ValueError("lat and lon must be float values")
        return super().db_value(value)


class PointListField(JSONField):
    """
    A JSON field that validates a list of points.
    Each point must be a dict with keys 'lat' and 'lon' that are floats.
    """

    def python_value(self, value):
        data = super().python_value(value)
        if data is None:
            return data
        if not isinstance(data, list):
            raise ValueError("PointListField expects a list of points")
        for point in data:
            if not isinstance(point, dict) or 'lat' not in point or 'lon' not in point:
                raise ValueError(
                    "Each point must be a dict with 'lat' and 'lon' keys")
            try:
                point['lat'] = float(point['lat'])
                point['lon'] = float(point['lon'])
            except (TypeError, ValueError):
                raise ValueError("lat and lon must be float values")
        return data

    def db_value(self, value):
        if value is None:
            return value
        if not isinstance(value, list):
            raise ValueError("PointListField expects a list of points")
        for point in value:
            if not isinstance(point, dict) or 'lat' not in point or 'lon' not in point:
                raise ValueError(
                    "Each point must be a dict with 'lat' and 'lon' keys")
            try:
                point['lat'] = float(point['lat'])
                point['lon'] = float(point['lon'])
            except (TypeError, ValueError):
                raise ValueError("lat and lon must be float values")
        return super().db_value(value)


class EnumField(CharField):
    """
    A field that stores an Enum value as a string in the database.
    """

    def __init__(self, enum_type, *args, **kwargs):
        self.enum_type = enum_type
        kwargs.setdefault('max_length', 50)
        super().__init__(*args, **kwargs)

    def python_value(self, value):
        if value is not None:
            try:
                return self.enum_type(value)
            except ValueError:
                raise ValueError(
                    f"Invalid value '{value}' for enum {self.enum_type}")
        return None

    def db_value(self, value):
        if isinstance(value, self.enum_type):
            return value.value
        return value
