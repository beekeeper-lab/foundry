# /run Command

Pulls the latest code from `main` and launches the desktop app.

## Usage

```
/run              # Pull main and run
/run main         # Pull main and run (explicit)
```

## Process

1. Auto-stash if dirty
2. Fetch, checkout, and pull `main`
3. Install/sync dependencies (`uv sync`)
4. Launch the app (`uv run <app-name>`)
5. After the app exits, restore the original branch and stash

Designed for running locally after dev work is pushed from a remote server.
