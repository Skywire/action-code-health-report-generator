# action-code-health-report-generator

Generate Code Health Check Report form
an [action-code-health-check](https://github.com/Skywire/action-code-health-check/) run

## Inputs

| Name           | Description                                                               | Required |
|----------------|---------------------------------------------------------------------------|----------|
| `client-name`  | Client Name for report                                                    | yes      |
| `repo-name`    | Client Repository Name                                                    | yes      |
| `run-id`       | Action Run ID containing code health artifacts                            | yes      |
| `github-token` | GitHub Token with permission to access the repository and its action runs | yes      |

## Usage

```yaml
  steps:
    - uses: Skywire/action-code-health-report-generator@main
      with:
        client-name: 'Example Client'
        repo-name: 'Skywire/exampleclient.com'
        run-id: ${ GITHUB_RUN_ID }
        github-token: ${{ secrets.GITHUB_TOKEN }}
```