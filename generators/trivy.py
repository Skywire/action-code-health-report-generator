import json

from mdutils import MdUtils


def generate_vulnerability_report(path: str, md: MdUtils) -> None:
    md.new_header(2, "Vulnerabilities")

    with open(path, "r") as f:
        report = json.load(f)
        if ('Results' not in report):
            md.write("No Results.")

            return
        rows = ["Target", "Vulnerability ID", 'Title', 'URL', 'Severity']
        for result in report['Results']:
            if ('Vulnerabilities' not in result):
                continue
            target = result['Target']
            for vuln in result['Vulnerabilities']:
                rows.extend([target, vuln['VulnerabilityID'], vuln['Title'],
                             vuln['PrimaryURL'] if 'PrimaryURL' in vuln else 'N/A', vuln['Severity']])

        md.new_table(5, int(len(rows) / 5), rows)


def generate_secret_report(path: str, md: MdUtils) -> None:
    md.new_header(2, "Secrets")

    with open(path, "r") as f:
        report = json.load(f)
        if ('Results' not in report):
            md.write("No Results.")

            return

        rows = ["Target", "Rule ID", 'Category', 'Title']
        for result in report['Results']:
            target = result['Target']

            if ('Secrets' not in result):
                continue
            for secret in result['Secrets']:
                rows.extend([target, secret['RuleID'], secret['Category'], secret['Title']])

        md.new_table(4, int(len(rows) / 4), rows)
