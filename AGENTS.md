# Portfolio repository

This is a public demonstration repository, not a copy of business systems.
Use synthetic fixtures only. Never add credentials, customer data, internal
URLs, IP addresses, recordings, source-system exports, or production logs.
Default demonstrations must work offline using the Python standard library.
Clearly distinguish simulations from real provider integrations.
Run `python3 -m unittest discover -s tests -v` and
`python3 tools/check_public_content.py` before committing or publishing.
Keep runtime output under `.demo-output/`; do not commit SQLite databases or audio.

This public repository is `bolesusi147-web/ai-automation-portfolio`.
Do not copy private Codespaces or job-search material from `Projects`.

README artwork must use synthetic content and be reviewed before publication.
The only approved binary assets are the three named PNG/GIF paths covered by
`assets/manifest.json` and `tools/check_public_content.py`. Do not broaden that
exception to recordings, real screenshots, exports or other binary files.
Keep the main README and recruiter guide relevant across companies; vendor-specific
notes are optional supporting materials. Visual authoring may use Pillow, but
the default demos, tests and publication checks must remain standard-library only.
