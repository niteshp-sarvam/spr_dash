import json


def to_json_download(data: dict, filename: str = "spr_export.json") -> tuple[str, str]:
    """Serialize data to a JSON string and return (json_string, filename)."""
    return json.dumps(data, indent=2, default=str), filename
