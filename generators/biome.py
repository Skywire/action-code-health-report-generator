import json

from mdutils import MdUtils

def generate_report(path: str, md: MdUtils) -> None:
    md.new_header(2, "Summary")

    with open(path, "r") as f:
        raw = f.read()
        raw = raw.replace("\n", "")
        report = json.loads(raw)
        summary = report["summary"]
        rows = ["Check", "Count"]
        for level, count in summary.items():
            rows.extend([level, count])

        md.new_table(2, int(len(rows) / 2), rows)