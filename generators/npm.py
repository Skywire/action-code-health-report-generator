import json
import os

from mdutils import MdUtils


def generate_audit_report(path: str, md: MdUtils) -> None:
    md.new_header(3, 'Audit')
    md.new_header(4, "Vulnerabilities")

    if not os.path.exists(path):
        md.write("No Results.")

        return

    with open(path, "r") as f:
        report = json.load(f)
        vuln = report["metadata"]["vulnerabilities"]
        rows = ["Level", "Count"]
        for level, count in vuln.items():
            rows.extend([level, count])

        md.new_table(2, int(len(rows) / 2), rows)


def generate_outdated_report(path: str, md: MdUtils) -> None:
    md.new_header(3, 'Outdated')

    if not os.path.exists(path):
        md.write("No Results.")

        return

    with open(path, "r") as f:
        report = json.load(f)

        if not report or len(report) == 0:
            md.write('0 Outdated Packages')

            return

        rows = ["Package", "Current", "Wanted", "Latest"]
        for package, details in report.items():
            rows.extend([package, details['current'], details['wanted'], details['latest']])

        md.new_table(4, int(len(rows) / 4), rows)
