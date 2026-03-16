import json
import os

from mdutils import MdUtils

def generate_report(path: str, md: MdUtils) -> None:
    md.new_header(3, "Summary")

    if not os.path.exists(path):
        md.write("No Results.")

        return

    with open(path, "r") as f:
        report = json.load(f)
        summary = report["statistics"]["total"]
        rows = ["Check", "Count"]
        for level, count in summary.items():
            rows.extend([level, count])

        md.new_table(2, int(len(rows) / 2), rows)