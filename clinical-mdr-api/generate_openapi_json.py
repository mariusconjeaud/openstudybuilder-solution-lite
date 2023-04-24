import json

from clinical_mdr_api.main import custom_openapi
from clinical_mdr_api.utils import increment_api_version_if_needed

api_spec_new: dict
api_spec_old: dict

with open("openapi.json", "r", encoding="utf-8") as f:
    api_spec_old = json.load(f)

api_spec_new = custom_openapi()

api_spec_new = increment_api_version_if_needed(api_spec_new, api_spec_old)

with open("openapi.json", "w", encoding="utf-8") as f:
    json.dump(
        api_spec_new,
        f,
        indent=2,
    )

with open("apiVersion", "w", encoding="utf-8") as f:
    f.write(api_spec_new["info"]["version"])

print("Successfully created openapi.json")
