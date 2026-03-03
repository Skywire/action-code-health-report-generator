# action-code-health-report-generator

Generate Code Health Check Report form
an [action-code-health-check](https://github.com/Skywire/action-code-health-check/) run

## Inputs

| Name                     | Description                                                               | Required |
|--------------------------|---------------------------------------------------------------------------|----------|
| `client-name`            | Client Name for report                                                    | yes      |
| `repo-name`              | Client Repository Name                                                    | yes      |
| `run-id`                 | Action Run ID containing code health artifacts                            | yes      |
| `shared-drive-id`        | Shared Google Drive ID to upload the report                               | yes      |
| `google-service-account` | Service account credentials JSON (usually stored as a secret)             | yes      |
| `github-token`           | GitHub Token with permission to access the repository and its action runs | yes      |

## Usage

```yaml
  steps:
    - uses: Skywire/action-code-health-report-generator@main
      with:
        client-name: 'Example Client'
        repo-name: 'Skywire/exampleclient.com'
        run-id: ${ GITHUB_RUN_ID }
        shared-drive-id: '1Ym86xTbfqIV-cPzL5ZCzcw3ftY1NWFks'
        google-service-account: ${{ secrets.GOOGLE_SERVICE_ACCOUNT }}
        github-token: ${{ secrets.GITHUB_TOKEN }}
```