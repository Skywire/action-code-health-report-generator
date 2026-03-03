import os
import sys
import urllib
import zipfile
from datetime import date
from os import environ

from dotenv import load_dotenv
from github import Auth, Github
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from mdutils import MdUtils
from oauth2client.service_account import ServiceAccountCredentials

from generators import npm, biome, mago, jscpd, trivy, gitleaks

from markdown_pdf import MarkdownPdf, Section

load_dotenv()

## TODO Get these from env and run args
client_name = environ.get('CLIENT_NAME')
repo_name = environ.get('REPO_NAME')
run_id = int(environ.get('RUN_ID'))
token = environ.get('GITHUB_TOKEN')
shared_drive_id = environ.get('SHARED_DRIVE_ID')


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


def upload_to_google_drive(path: str):
    creds = ServiceAccountCredentials.from_json_keyfile_name('var/credentials/google-service-account.json')

    if not creds or creds.invalid:
        print('Unable to authenticate using service account key.')
        sys.exit()

    service = build('drive', 'v3', credentials=creds)

    file_metadata = {'name': f"{date.today().strftime('%b %d %Y')}-client-report.pdf", 'parents': [shared_drive_id]}
    media = MediaFileUpload(path, mimetype='application/pdf')

    f = service.files().create(body=file_metadata, media_body=media, supportsAllDrives=True).execute()

    # application / vnd.google - apps.document
    files = service.files()
    files.update(fileId=f['id'], supportsAllDrives=True, media_mime_type='application/vnd.google-apps.document').execute()

    print("Created file '%s' id '%s'." % (f.get('name'), f.get('id')))
    pass

def create_pdf(markdown_path, pdf_path):
    css = """
  @page { margin: 2cm; size: A4; }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    font-size: 14px;
    line-height: 1.6;
    color: #1a1a2e;
    background: #fff;
    max-width: 900px;
    margin: 0 auto;
    padding: 40px 32px;
  }

  /* Header */
  .report-header {
    border-bottom: 3px solid #1a1a2e;
    padding-bottom: 20px;
    margin-bottom: 32px;
  }
  .report-header .label {
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #666;
    margin-bottom: 4px;
  }
  .report-header h1 {
    font-size: 20px;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 6px;
  }
  .report-header .subtitle {
    font-size: 16px;
    color: #444;
  }
  .meta-row {
    display: flex;
    gap: 32px;
    margin-top: 14px;
    font-size: 13px;
    color: #555;
  }
  .meta-row strong { color: #1a1a2e; }

  /* Classification banner */
  .classification {
    background: #fef3cd;
    border: 1px solid #ffc107;
    border-radius: 4px;
    padding: 10px 16px;
    font-size: 13px;
    font-weight: 600;
    text-align: centre;
    margin-bottom: 28px;
    color: #856404;
  }

  /* Sections */
  h2 {
    font-size: 19px;
    font-weight: 700;
    color: #1a1a2e;
    margin-top: 36px;
    margin-bottom: 14px;
    padding-bottom: 6px;
    border-bottom: 1px solid #ddd;
  }
  h3 {
    font-size: 16px;
    font-weight: 600;
    color: #2d2d4e;
    margin-top: 24px;
    margin-bottom: 10px;
  }
  p { margin-bottom: 12px; }

  /* Executive summary box */
  .exec-summary {
    background: #f0f4ff;
    border-left: 4px solid #2563eb;
    padding: 18px 22px;
    border-radius: 0 6px 6px 0;
    margin-bottom: 28px;
  }
  .exec-summary p { margin-bottom: 8px; }
  .exec-summary p:last-child { margin-bottom: 0; }
  .exec-summary strong { color: #1e40af; }

  /* Key finding boxes */
  .finding {
    background: #fafafa;
    border: 1px solid #e5e5e5;
    border-radius: 6px;
    padding: 20px 24px;
    margin-bottom: 20px;
  }
  .finding-header {
    display: flex;
    align-items: centre;
    gap: 10px;
    margin-bottom: 12px;
  }
  .finding-header .tag {
    display: inline-block;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 2px 8px;
    border-radius: 3px;
  }
  .tag-critical { background: #fee2e2; color: #991b1b; }
  .tag-high     { background: #fef3cd; color: #856404; }
  .tag-medium   { background: #d1ecf1; color: #0c5460; }
  .tag-info     { background: #e2e3e5; color: #383d41; }

  /* Tables */
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 14px 0 18px 0;
    font-size: 13px;
  }
  th, td {
    text-align: left;
    padding: 8px 12px;
    border-bottom: 1px solid #e5e5e5;
  }
  th {
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #555;
  }
  tr:last-child td { border-bottom: none; }
  td code {
    background: #f0f0f0;
    padding: 1px 5px;
    border-radius: 3px;
    font-size: 12px;
    font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  }

  /* Indicator list */
  .indicators {
    list-style: none;
    padding: 0;
  }
  .indicators li {
    padding: 8px 0 8px 24px;
    position: relative;
    border-bottom: 1px solid #f0f0f0;
  }
  .indicators li::before {
    content: '';
    position: absolute;
    left: 4px;
    top: 14px;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #dc3545;
  }
  .indicators li:last-child { border-bottom: none; }
  .indicators li strong { color: #1a1a2e; }

  /* Recommendations */
  .recommendation {
    display: flex;
    gap: 14px;
    padding: 12px 0;
    border-bottom: 1px solid #f0f0f0;
  }
  .recommendation:last-child { border-bottom: none; }
  .rec-number {
    flex-shrink: 0;
    width: 28px;
    height: 28px;
    background: #1a1a2e;
    color: #fff;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    font-weight: 700;
  }
  .rec-content { flex: 1; }
  .rec-content strong { color: #1a1a2e; }

  /* Timing chart */
  .timeline {
    background: #fafafa;
    border: 1px solid #e5e5e5;
    border-radius: 6px;
    padding: 16px 20px;
    margin: 14px 0;
    font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
    font-size: 12px;
    line-height: 2;
    white-space: pre;
    overflow-x: auto;
  }

  /* Print styles */
  @media print {
    body { padding: 0; font-size: 12px; }
    .finding { break-inside: avoid; }
    h2 { break-after: avoid; }
  }
    """

    with open(markdown_path, 'r') as f:
        markdown_content = f.read()

    pdf = MarkdownPdf()
    pdf.meta["title"] = f"{client_name} | Code Health Report {date.today().strftime('%b %d %Y')}"
    pdf.add_section(Section(markdown_content, toc=False), user_css=css)
    pdf.save(pdf_path)

if __name__ == "__main__":
    download_artifacts()

    md = MdUtils(file_name='var/output/report.md')

    md.new_header(1, f"{client_name} | Code Health Report {date.today().strftime('%b %d %Y')}")

    md.new_header(2, 'NPM')
    npm.generate_audit_report("var/reports/npm-audit.json", md)
    npm.generate_outdated_report("var/reports/npm-outdated.json", md)

    md.new_header(2, 'Biome')
    biome.generate_report("var/reports/biome-check.json", md)

    md.new_header(2, 'Mago')
    mago.generate_analyse_report("var/reports/mago-analyze-code-count.txt", md)
    mago.generate_lint_report("var/reports/mago-lint-code-count.txt", md)

    md.new_header(2, 'JSCPD')
    jscpd.generate_report("var/reports/jscpd-report.json", md)

    md.new_header(2, 'Trivy')
    trivy.generate_vulnerability_report("var/reports/trivy-report.json", md)
    trivy.generate_secret_report("var/reports/trivy-report.json", md)

    md.new_header(2, 'Gitleaks')
    gitleaks.generate_report("var/reports/work", md)

    md.create_md_file()

    create_pdf('var/output/report.md', 'var/output/report.pdf')

    upload_to_google_drive('var/output/report.pdf')
