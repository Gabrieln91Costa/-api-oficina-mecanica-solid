from pathlib import Path
import json
import yaml

root = Path(__file__).resolve().parents[1]
json.loads((root / "postman/collection.json").read_text(encoding="utf-8"))
for path in (root / "k8s").glob("*.yaml"):
    list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
print("Collection Postman e manifestos Kubernetes: sintaxe válida.")
