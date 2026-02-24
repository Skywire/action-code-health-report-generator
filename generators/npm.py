import json

from mdutils import MdUtils


def generate_audit_report(path: str, md: MdUtils) -> None:
    md.new_header(2, 'Audit')
    md.new_header(3, "Vulnerabilities")

    with open(path, "r") as f:
        report = json.load(f)
        vuln = report["metadata"]["vulnerabilities"]
        rows = ["Level", "Count"]
        for level, count in vuln.items():
            rows.extend([level, count])

        md.new_table(2, int(len(rows) / 2), rows)


def generate_outdated_report(path: str, md: MdUtils) -> None:
    md.new_header(2, 'Outdated')

    with open(path, "r") as f:
        report = json.load(f)

        if not report:
            md.write('0 Outdated Packages')
