# R Security

Security practices for R projects: credential handling, safe database
access, defensive evaluation of user-supplied expressions, and package
supply-chain hygiene. R's research-and-analysis culture has historically
been lax about secrets and untrusted input — these are the defaults that
fix that.

---

## Defaults

| Concern              | Default Tool / Approach                  |
|----------------------|------------------------------------------|
| Credential storage   | `keyring` (OS keychain) for interactive; env vars for CI |
| Project env vars     | `.Renviron` (gitignored), loaded by R at startup |
| Database access      | `DBI` + parameterised queries (`dbBind` / `dbGetQuery(... params = list(...))`) |
| HTTP client          | `httr2` (modern) or `httr` (legacy)      |
| Untrusted input      | Never `eval(parse(text = ...))`; use a parser or whitelist |
| Lockfile             | `renv.lock` committed; CI verifies via `renv::status()` |
| Package source vetting | CRAN / Bioconductor first; pin GitHub installs to SHA |
| Static analysis      | `lintr` rules + `oysteR` (CVE check)     |
| Logging              | `logger` package; redact secrets at the source |

### Alternatives

- **`config`** package — layered config files. Useful for non-secret
  environment selection (dev / staging / prod); secrets still belong in
  `keyring` / env vars.
- **`vault`** package — HashiCorp Vault client for orgs with a secrets
  service. Use when keyring is insufficient (machine identities, dynamic
  credentials).
- **`pak`** — has a stricter dependency resolver than `install.packages` and
  is a good signal-checker for unexpected deps.

---

## Secrets Management

**Rule: No secrets in source files, `.Rprofile`, `DESCRIPTION`, or notebook
output.**

```r
# BAD — hardcoded secret
api_key <- "sk-live-abc123"

# BAD — fallback default that ships with the code
api_key <- Sys.getenv("API_KEY", unset = "sk-live-abc123")

# GOOD — fail fast if not configured (use unset = NA + check)
api_key <- Sys.getenv("API_KEY", unset = NA)
if (is.na(api_key)) {
  rlang::abort("API_KEY is not set in the environment")
}

# BETTER — pull from OS keychain interactively
library(keyring)
api_key <- keyring::key_get("my-service", "api-key")
```

### Storing credentials with keyring

```r
# Store once (interactive prompt for the value)
keyring::key_set("postgres", "analytics-prod")

# Retrieve in scripts and functions
pwd <- keyring::key_get("postgres", "analytics-prod")
```

`keyring` uses macOS Keychain, Windows Credential Store, or Linux Secret
Service depending on platform. Falls back to a local encrypted file if
none is available.

### `.Renviron` for non-secret environment

```
# .Renviron — committed to .gitignore, NOT to the repo
DB_HOST=analytics.example.com
DB_PORT=5432
DB_NAME=analytics
DB_USER=app_reader
# No DB_PASSWORD here — that comes from keyring or vault
```

R sources `.Renviron` automatically at startup. Keep secrets out of it
unless your org has a documented policy that says otherwise — even
`.gitignore`d files end up in screenshots, logs, and email.

### `.Rprofile` rules

`.Rprofile` runs on every R session start. Treat it like a shell rc file:

- **Do not** put secrets in it.
- **Do not** put `setwd()` or `library()` calls that surprise collaborators.
- **Do** keep it minimal — the project-local `.Rprofile` should source
  `renv/activate.R` and nothing else.

---

## Safe Database Access with DBI

Always use parameterised queries. Never build SQL with `paste()`, `glue()`,
or `sprintf()`.

```r
library(DBI)
con <- dbConnect(
  RPostgres::Postgres(),
  host = Sys.getenv("DB_HOST"),
  dbname = Sys.getenv("DB_NAME"),
  user = Sys.getenv("DB_USER"),
  password = keyring::key_get("postgres", "analytics-prod")
)

# BAD — SQL injection via string interpolation
result <- dbGetQuery(con, paste0("SELECT * FROM users WHERE id = '", user_id, "'"))
result <- dbGetQuery(con, glue::glue("SELECT * FROM users WHERE id = '{user_id}'"))

# GOOD — parameterised query, $1 placeholder (PostgreSQL/SQLite)
result <- dbGetQuery(
  con,
  "SELECT * FROM users WHERE id = $1",
  params = list(user_id)
)

# GOOD — ? placeholder (MySQL, ODBC)
result <- dbGetQuery(
  con,
  "SELECT * FROM users WHERE id = ?",
  params = list(user_id)
)
```

For dynamic SQL where structure (table names, column names) varies, use
`dbQuoteIdentifier()`:

```r
table <- dbQuoteIdentifier(con, user_supplied_table)
# Compose only AFTER quoting; never inline user-supplied identifiers.
sql <- paste0("SELECT * FROM ", table, " WHERE id = $1")
result <- dbGetQuery(con, sql, params = list(id))
```

---

## Untrusted Input — Never `eval(parse())`

`eval(parse(text = ...))` executes arbitrary R code. On any path where the
input comes from a user, file, network, or process you do not control, this
is remote code execution.

```r
# BAD — RCE vector
expr <- readLines("user-config.txt")
result <- eval(parse(text = expr))

# GOOD — parse to a known schema, validate, then dispatch
config <- yaml::read_yaml("user-config.txt")
stopifnot(
  is.character(config$operation),
  config$operation %in% c("sum", "mean", "median")
)
operation <- switch(config$operation,
  sum    = sum,
  mean   = mean,
  median = median
)
result <- operation(values)
```

The same rule applies to:

- `source()` on files whose contents could be modified by an attacker.
- `do.call()` with a function name pulled from input (`do.call(input$fn, args)`).
- `rlang::parse_expr()` and tidy-eval helpers when the input is untrusted.

**If you genuinely need a sandboxed evaluator** (e.g., a calculator app),
use the `RestrictedSEXP` pattern: parse to an AST, walk it rejecting any
call that is not in an allowlist, then evaluate.

---

## Safe HTTP Clients

Always set timeouts and verify TLS. `httr2` is the modern client and the
recommended default.

```r
library(httr2)

resp <- request("https://api.example.com/data") |>
  req_headers(Authorization = paste("Bearer", api_key)) |>
  req_timeout(seconds = 30) |>
  req_retry(max_tries = 3, backoff = ~ 2 ^ .x) |>
  req_perform()

# Disable redirects unless you trust the destination chain
resp <- request("https://api.example.com/data") |>
  req_options(followlocation = FALSE) |>
  req_perform()
```

Never disable TLS verification (`config(ssl_verifypeer = FALSE)`) in
production. If a self-signed certificate is genuinely required, pin the
specific certificate via `req_options(cainfo = "path/to/cert.pem")`.

---

## File Path Safety

User-supplied filenames must be validated before they are joined to a
trusted base directory.

```r
upload_dir <- "/var/app/uploads"

safe_file_path <- function(user_filename) {
  candidate <- normalizePath(file.path(upload_dir, user_filename), mustWork = FALSE)
  if (!startsWith(candidate, normalizePath(upload_dir))) {
    rlang::abort("Path traversal attempt detected", filename = user_filename)
  }
  candidate
}
```

`normalizePath()` resolves `..` and symlinks; the prefix check rejects any
result that escapes the upload directory.

---

## Package Supply Chain

R packages are arbitrary code with full filesystem and network access at
install time. Vet your sources.

### Source preference order

1. **CRAN** — packages have passed `R CMD check` and an automated review.
2. **Bioconductor** — same, with stricter genomics-domain conventions.
3. **R-universe / Posit Package Manager** — org-curated mirrors.
4. **GitHub via `remotes::install_github`** — only with a pinned tag/SHA.
5. **Random Gist or zip file** — never.

### Lockfile discipline

`renv.lock` records the exact version and source of every package. CI must
verify the environment matches the lockfile:

```r
# CI check — fails if the installed library drifts from renv.lock
renv::status()  # returns invisibly; non-empty messages = drift
```

### Vulnerability scanning

```r
# oysteR queries the Sonatype OSS Index for known CVEs in installed packages
oysteR::audit_installed_r_pkgs()

# Run weekly in CI; fail the build on any critical-severity finding
```

For higher-stakes orgs, route installs through Posit Package Manager,
which provides a curated mirror with SBOM tracking.

---

## Do / Don't

**Do:**

- Use `keyring` for interactive credential storage; env vars for CI.
- Source `.Renviron` for non-secret environment; never commit it.
- Use parameterised queries for all DB access (`DBI` `params = list(...)`).
- Set explicit timeouts on every HTTP request (`req_timeout()`).
- Pin GitHub installs to a tag or SHA; never to a branch name.
- Run `oysteR::audit_installed_r_pkgs()` (or equivalent) weekly in CI.
- Validate user-supplied filenames with `normalizePath()` + prefix check.
- Audit `.Rprofile` and `Rprofile.site` for surprises before adopting a
  new project.

**Don't:**

- Hardcode credentials, API keys, or DB passwords in source.
- Use `Sys.getenv("KEY", unset = "default-secret")` — the fallback ships
  in your code as the live key for any unset environment.
- Build SQL with `paste()`, `glue::glue()`, or `sprintf()`.
- Call `eval(parse(text = ...))`, `source()`, or `do.call()` on input you
  did not produce yourself.
- Disable TLS verification in production HTTP clients.
- Install packages from arbitrary URLs without checking provenance.
- Commit `.Renviron`, `.Rhistory`, or `.RData` — they may contain secrets.
- Print credentials, tokens, or query parameters to the console or logs.

---

## Common Pitfalls

1. **`Sys.getenv("KEY", unset = "default")` shipping a secret.** The fallback
   is in your code. In any environment without `KEY` set, that fallback IS
   the key. Always use `unset = NA` and explicitly check.

2. **Passwords in `.Rhistory`.** R records every interactive command. If
   you ever pasted a password at the prompt, it is in `~/.Rhistory`. Add
   `.Rhistory` and `.RData` to global gitignore and clear them after any
   credential-handling session.

3. **`glue::glue()` for SQL.** `glue` looks like a parameterised query but
   is just string interpolation — it does not escape SQL metacharacters.
   Use `dbGetQuery(con, sql, params = list(...))` instead.

4. **`source()` on a downloaded script.** `source("https://...")` runs
   whatever the server returns at that moment. If the server is
   compromised, so is your machine. Download, inspect, then `source()` the
   local copy with a known SHA.

5. **`eval(parse(text = ...))` in a "safe" context.** It is never safe.
   Even formula strings (`"y ~ x"`) should go through `as.formula()`, not
   parse-and-eval — the latter accepts arbitrary code.

6. **Forgetting that `.Rprofile` runs as the user.** A malicious package
   that modifies the project `.Rprofile` runs every time anyone opens
   the project. Code review changes to `.Rprofile` and `Rprofile.site`
   like you would `~/.bashrc`.

7. **Caching API responses to disk in clear text.** `memoise::cache_disk()`
   stores values verbatim. If the cached value contains tokens or PII,
   those are now plaintext on disk. Encrypt or scrub before caching.

8. **`renv::restore()` without verifying the lockfile source.** `renv.lock`
   records source URLs; an attacker who controls a GitHub install URL can
   substitute code on a tag move. Pin to commit SHAs, not tags, for any
   non-CRAN install in security-sensitive projects.

---

## Checklist

- [ ] No hardcoded secrets in source, `.Rprofile`, `DESCRIPTION`, or notebooks
- [ ] `keyring` used for interactive credential retrieval; env vars in CI
- [ ] `.Renviron` is gitignored; secrets are not in it
- [ ] All DB queries are parameterised (`params = list(...)`); no `paste()` SQL
- [ ] All HTTP clients set explicit timeouts and verify TLS
- [ ] No `eval(parse(text = ...))`, `source(<url>)`, or `do.call()` on input
- [ ] User-supplied paths validated with `normalizePath()` + prefix check
- [ ] GitHub installs pinned to tag or commit SHA
- [ ] `renv.lock` committed; CI verifies with `renv::status()`
- [ ] Vulnerability scan (`oysteR` or PPM SBOM) runs at least weekly in CI
- [ ] `.Rhistory`, `.RData`, `.Renviron` in global gitignore
- [ ] Logs reviewed to confirm no tokens, passwords, or PII are emitted
- [ ] `.Rprofile` changes go through code review
