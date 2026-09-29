# Contributing

Thanks for helping. The most useful contribution is a new job source.

## Ground rules

These keep job-scout free and safe to run. PRs that break them won't be merged.

- **No paid APIs, scraping services, or proxies.** Every source must be free to use.
- **No LLM calls in the daily pipeline.** Matching stays deterministic.
- **Respect access controls.** Don't bypass logins, CAPTCHAs, paywalls, rate limits, or `robots.txt`. Prefer official APIs, then RSS/Atom, then public ATS endpoints.
- **Keep dependencies minimal.** The Python standard library comes first, and a new package needs a reason in the PR.

## Adding a source adapter

1. Create `src/adapters/<name>.py` with a class that inherits `SourceAdapter` from `src/adapters/base.py`.
2. Set `name` and `source_type` (`api`, `rss`, `ats`, `social`, or `search_discovery`).
3. Implement `fetch()`. Use `self._get(url)`, which gives you the timeout, retries, and User-Agent.
4. Implement `normalize(raw)`. Return a list built with `self.make_job(...)`. Every job needs `title`, `company`, and `application_url`, or it's rejected.
5. Register the class in `ADAPTER_REGISTRY` in `src/adapters/__init__.py`.
6. Add the source to `config.example.json`, with `"enabled": true` and any options it takes.
7. Add a `normalize()` test to `tests/test_adapters.py` using a small fixture payload. Tests must not make network calls.
8. Add a row to the Sources table in `README.md`.

If the API needs a free key, read it from an environment variable, skip cleanly when it's missing, and document the secret in the README.

## Development

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -q
cp config.example.json config.json && cp profile.example.json profile.json
DRY_RUN=1 python -m src.pipeline   # prints the email instead of sending it
```

A `DRY_RUN` still writes to `data/jobs.db`. Delete that file afterwards so you don't mark real jobs as already seen.

## Pull requests

- Keep each PR to one source or one fix.
- Tests must pass. CI runs them on every PR.
- Include the `[<name>] fetched=… accepted=…` line from a local dry run when you add a source.
