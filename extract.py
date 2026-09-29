import base64
import json
import zlib
import re

with open("main.py") as f:
    code = f.read()

match = re.search(r"_V55_MODULES\s*=\s*json\.loads\(zlib\.decompress\(base64\.b85decode\(\s*\(\s*(.*?)\s*\)\s*\)\)\.decode\(\"utf-8\"\)\)", code, re.DOTALL)
if match:
    s = match.group(1).replace("'", "").replace("\n", "").replace(" ", "")
    modules = json.loads(zlib.decompress(base64.b85decode(s)).decode("utf-8"))
    import os
    os.makedirs("extracted_v55", exist_ok=True)
    for name, source in modules.items():
        path = os.path.join("extracted_v55", name.replace(".", "/") + ".py")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as out:
            out.write(source)
    print("Extracted", len(modules), "modules")
else:
    print("Match not found")
