import json

from mdutils import MdUtils

def generate_report(path: str, md: MdUtils) -> None:
    md.new_header(3, "Summary")

    with open(path, "r") as f:
        raw = f.read()
        raw = raw.replace("\n", "")
        try:
            report = json.loads(raw)
            summary = report["summary"]
            rows = ["Check", "Count"]
            for level, count in summary.items():
                rows.extend([level, count])

            md.new_table(2, int(len(rows) / 2), rows)
        except json.JSONDecodeError:
            md.write("No Results.")