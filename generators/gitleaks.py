import glob
import json

from mdutils import MdUtils


def generate_report(path: str, md: MdUtils) -> None:
    file_path = glob.glob(f"{path}/**/*.sarif", recursive=True).pop()
    with open(file_path, "r") as f:
        runs = json.load(f)['runs']

        rows = ["Message", "Rule", "Location"]
        for run in runs:
            results = run["results"]
            for result in results:
                message = result["message"]["text"]
                rule = result["ruleId"]
                for location in result["locations"]:
                    rows.extend([message, rule, location["physicalLocation"]["artifactLocation"]["uri"]])

        if (len(rows) == 3):
            md.new_line("No secrets found.")
        else:
            md.new_table(3, int(len(rows) / 3), rows)
