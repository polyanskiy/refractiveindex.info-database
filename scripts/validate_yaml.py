import sys
import json
import yaml
from jsonschema import validate, ValidationError

schema_path = "schemas/data.schema.json"

with open(schema_path) as f:
    schema = json.load(f)

errors = False

for path in sys.argv[1:]:
    try:
        with open(path) as f:
            data = yaml.safe_load(f)

        validate(instance=data, schema=schema)
        print(f"✓ {path}")

    except ValidationError as e:
        errors = True
        print(f"✗ {path}")
        print(f"  {e.message}")

    except Exception as e:
        errors = True
        print(f"✗ {path}")
        print(f"  {str(e)}")

if errors:
    sys.exit(1)
