import urllib
import zipfile
from datetime import date
from os import environ

from dotenv import load_dotenv
from github import Auth, Github
from mdutils import MdUtils

from generators import npm, biome, mago, jscpd, trivy, gitleaks

load_dotenv()

## TODO Get these from env and run args
client_name = environ.get('CLIENT_NAME')
repo_name = environ.get('REPO_NAME')
run_id = int(environ.get('RUN_ID'))
token = environ.get('GITHUB_TOKEN')


def download_artifacts():
    auth = Auth.Token(token)
    g = Github(auth=auth)

    artifacts = g.get_repo(repo_name).get_workflow_run(run_id).get_artifacts()
    for artifact in artifacts:
        filename = f"{artifact.name}.zip"
        status, headers, response = g.requester.requestJson("GET", artifact.archive_download_url)
        if status == 302:
            urllib.request.urlretrieve(headers['location'], f"var/tmp/{filename}")
            with zipfile.ZipFile(f"var/tmp/{filename}", 'r') as f:
                f.extractall("var/reports")
    g.close()


if __name__ == "__main__":
    download_artifacts()

    md = MdUtils(file_name='var/output/report.md',
                 title=f"{client_name} | Code Health Report for {date.today().strftime('%B %d, %Y')}")

    md.new_header(1, 'NPM')
    npm.generate_audit_report("var/reports/npm-audit.json", md)
    npm.generate_outdated_report("var/reports/npm-outdated.json", md)

    md.new_header(1, 'Biome')
    biome.generate_report("var/reports/biome-check.json", md)

    md.new_header(1, 'Mago')
    mago.generate_analyse_report("var/reports/mago-analyze-code-count.txt", md)
    mago.generate_lint_report("var/reports/mago-lint-code-count.txt", md)

    md.new_header(1, 'JSCPD')
    jscpd.generate_report("var/reports/jscpd-report.json", md)

    md.new_header(1, 'Trivy')
    trivy.generate_vulnerability_report("var/reports/trivy-report.json", md)
    trivy.generate_secret_report("var/reports/trivy-report.json", md)

    md.new_header(1, 'Gitleaks')
    gitleaks.generate_report("var/reports/work", md)

    md.create_md_file()
