# Shell Policy

## Rules

- `sudo` is **denied**. No elevated privileges.
- Package installation (`pip install`, `npm install`) is **allowed**.
- `rm -rf` is **denied**. Use targeted file removal only.
- `git reset --hard` is **denied**. Preserve working tree state.
