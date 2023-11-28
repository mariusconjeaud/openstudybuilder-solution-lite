import json

from clinical_mdr_api.main import custom_openapi
from clinical_mdr_api.utils.api_version import (
    increment_api_version_if_needed,
    increment_version_number,
)

api_spec_new: dict
api_spec_old: dict


api_spec_new = custom_openapi()
try:
    with open("openapi.json", "r", encoding="utf-8") as f:
        api_spec_old = json.load(f)
    api_spec_new = increment_api_version_if_needed(api_spec_new, api_spec_old)
except FileNotFoundError:
    with open("apiVersion", encoding="utf-8") as f:
        old_version = f.read().strip()
    new_version = increment_version_number(old_version)
    api_spec_new["info"]["version"] = new_version
    print(f"No openapi.json found, read version {old_version} from the apiVersion file")

with open("openapi.json", "w", encoding="utf-8") as f:
    json.dump(
        api_spec_new,
        f,
        indent=2,
    )

with open("apiVersion", "w", encoding="utf-8") as f:
    f.write(api_spec_new["info"]["version"])

print("Successfully created openapi.json")
