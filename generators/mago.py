from mdutils import MdUtils


def generate_analyse_report(path: str, md: MdUtils) -> None:
    md.new_header(2, 'Analyse')

    __generate_code_count_report(path, md)


def generate_lint_report(path: str, md: MdUtils) -> None:
    md.new_header(2, 'Lint')

    __generate_code_count_report(path, md)


def __generate_code_count_report(path: str, md: MdUtils) -> None:
    with open(path, "r") as f:
        report = f.readlines()
        report = [line.strip() for line in report if line.strip()]
        report = [line.split(': ') for line in report]
        rows = ["Type", "Check", "Count"]
        for issue, count in report:
            type, check = issue.strip(']').split('[')
            rows.extend([type, check, count])

        md.new_table(3, int(len(rows) / 3), rows)
