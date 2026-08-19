# Pipeline Status Board

The `Publish Pipeline Status Board` workflow publishes the latest 100 EventHub GitHub Actions runs to GitHub Pages. It is intentionally manual so the board only changes when requested.

## First-time setup

1. A repository administrator must enable GitHub Pages under **Settings → Pages** and select **GitHub Actions** as the source. The workflow token cannot create the Pages site.
2. Run `Publish Pipeline Status Board` from the Actions tab.
3. Open the Pages URL shown in the completed workflow.

The board uses a token-free published `status-data.json` snapshot. Selecting a run opens the corresponding GitHub Actions run page.

<img src="assets/pipeline-success.gif" width="560" alt="Successful pipeline run">

## Local development

Open PowerShell at the repository root and run:

```powershell
python -m http.server 8000 --directory pipeline-tracker
```

Open `http://127.0.0.1:8000/`. The local page displays data after the Pages workflow has generated and published `status-data.json`.

Stop the server with `Ctrl+C`.

## Status filters

Use the buttons to filter all, successful, failed, running, or queued runs. Each run shows its workflow name, branch, event, timestamp, run number, and direct GitHub Actions link.

The status buttons use the same visual cues as the DevTrack board: `pipeline-success.gif` for successful runs, `office.gif` for failed runs, `pipeline-running.gif` for running runs, and `pipeline-queued.gif` for queued runs.

## Refreshing the board

Run the workflow again whenever you need a fresh snapshot. If the board reports that no snapshot is available, verify that GitHub Pages uses **GitHub Actions** as its source and rerun the publisher.

## If the dashboard stops

1. Inspect the latest `Publish Pipeline Status Board` run in the Actions tab.
2. If `Verify GitHub Pages is enabled` fails, or `configure-pages` reports `Get Pages site failed`, an administrator must open **Settings → Pages**, select **GitHub Actions** as the source, save, and rerun the workflow.
3. If upload or deployment fails, inspect the step log and rerun the workflow.
4. If the site returns 404, confirm the workflow copied `pipeline-tracker/index.html` to the artifact root.
5. Confirm `status-data.json` was generated before the Pages artifact was uploaded.
