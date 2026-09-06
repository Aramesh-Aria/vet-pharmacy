<!--
================================================================
  README TEMPLATE — recruiter-facing project repositories
  Written against your three repos: vet-pharmecy, AcaSmart-repo,
  ArameshMusicAcademy-website. The examples below are real ones
  from your own projects, not generic filler.

  How to use:
   1. Copy to the repo root as README.md
   2. Replace every <...> placeholder
   3. Delete sections that genuinely do not apply
   4. Never delete "Key design decisions" — it is the whole point
   5. Delete these comment blocks before committing

  Your vet-pharmecy README already covers deployment better than
  most junior repos. What it is missing is the top of the file:
  a reviewer opening it cannot tell in ten seconds what the project
  is for, what state it is in, or what you decided and why. That is
  what sections 1–5 below fix.
================================================================
-->

# <ProjectName>

<One sentence: what it does and who it is for.>

**Status:** <in production / in development, pre-launch> &nbsp;·&nbsp;
🔗 **Live:** <https://example.com — or "not public yet"> &nbsp;·&nbsp;
📦 **Releases:** <7> &nbsp;·&nbsp;
🧪 **Tests:** <pytest — what is covered>

<!-- Say "in development" out loud. Hiding it looks worse than owning it. -->

---

## Screenshots

<!-- 2 images maximum, near the top. A reviewer decides in ten seconds.
     If there is no UI yet, put a data-model diagram or an admin screenshot
     here instead. Never leave this section empty. -->

![<Main view>](docs/images/<main>.png)
![<Second view>](docs/images/<second>.png)

---

## Problem

<2–3 sentences on the real situation before the software existed.

 Example (vet-pharmecy): The clinic takes drug orders, prescription refills
 and appointment requests over the phone and on paper, so vaccination due
 dates are tracked by memory and refills are frequently missed.>

## What I built

<2–3 sentences on the solution and its current state.

 Example: A Persian, right-to-left Django application covering the product
 catalogue, animal records, cart and order lifecycle, prescriptions,
 appointments and visit records, with SMS notifications built on a pluggable
 backend. Backend-first: <N> apps implemented, deployment configured on
 RunFlare, public launch pending <what you are waiting on>.>

**My role:** <Sole developer — requirements, data model, architecture, implementation, tests and deployment.>

---

## Architecture

<!-- For a Django project, the app table is the architecture. Keep the table
     you already have and add the flow paragraph underneath — the table shows
     what exists, the paragraph shows that you understand how it moves. -->

| App | Responsibility |
|---|---|
| `config` | <split settings (base/dev/prod), URLs, WSGI/ASGI> |
| `accounts` | <custom User with phone identity, owner profiles, OTP auth> |
| `core` | <base templates, Jalali/Persian template filters> |
| `<app>` | <what it owns> |

<One paragraph tracing a single real action end to end.

 Example: When an owner requests a prescription refill, the view in
 `pharmacy` validates the prescription against its remaining refills and
 expiry, creates a RefillRequest in a pending state, and calls `notify()` in
 `notifications` rather than any SMS client directly. The delivery backend is
 selected from settings, so switching SMS providers touches one module and no
 view code.>

**Non-Django projects** — show the layer tree instead:

```
<project>/
├── core/      # domain models and business rules, imports no UI
├── db/        # single access layer — all SQL lives here
├── ui/        # presentation only, no business logic
└── tests/
```

---

## Key design decisions

<!-- The single most valuable section for a technical reviewer, and the
     source of most of your interview questions. 3–5 rows.
     Every row must name a trade-off you actually accepted.
     If you already keep ADRs, link each row to its ADR file. -->

| Decision | Why | Trade-off accepted |
|---|---|---|
| <Phone number as the user identity instead of email> ([ADR-0004](docs/adr/0004-...md)) | <Clients are Iranian owners and farmers who reliably have a mobile number, not an email address> | <Login depends on an SMS provider being up and costs money per message> |
| <Notification layer behind a `notify()` interface with pluggable backends> ([ADR-0003](docs/adr/0003-...md)) | <SMS provider can be swapped, and tests run against a dummy backend with no network> | <One more indirection than calling the SMS client directly> |
| <Pay at pickup instead of an online gateway in v1> ([ADR-0005](docs/adr/0005-...md)) | <A payment gateway requires e-Namad, which the client does not have yet; the rest of the product ships without it> | <Orders are not settled in the system; online payment is deferred to a later phase> |
| <Split settings into base/dev/prod> | <Same codebase runs on SQLite locally and PostgreSQL in production without edits> | <Three files to keep in sync instead of one> |
| <Deployed from git on RunFlare without Docker> | <Iranian PaaS with the shortest path to a running site for a single small client> | <Less portable than a container; environment is defined by the platform, not the repo> |

<!-- AcaSmart rows you can reuse:
 | SQLite over a client/server database | single-machine desktop app, zero-config install for a non-technical user | no concurrent multi-user access; would migrate if the academy opens a second branch |
 | Central DB access layer instead of SQL in widgets | schema changes touch one file and the UI becomes testable | extra indirection for trivial reads |
 | Separate x86 and arm64 builds | users are on both Intel Windows and Apple Silicon | the release pipeline runs twice per version |
-->

---

## Tech stack

- **Language:** <Python 3.11>
- **Framework:** <Django 5.2 / PySide6>
- **Database:** <PostgreSQL in production, SQLite in local development>
- **Serving:** <Gunicorn + WhiteNoise>
- **Deployment:** <RunFlare, deployed straight from the git repo>
- **Other:** <Jalali calendar support, django-simple-captcha, Pillow>

---

## Getting started

```bash
git clone https://github.com/Aramesh-Aria/<repo>.git
cd <repo>
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env        # then fill in the values
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

**Environment variables**

| Variable | Purpose |
|---|---|
| `DJANGO_SETTINGS_MODULE` | `config.settings.dev` locally, `config.settings.prod` in production |
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` locally, `False` in production |
| `DATABASE_URL` | PostgreSQL connection string in production |
| `ALLOWED_HOSTS` | comma-separated hostnames |
| `<SMS_API_KEY>` | <external service this project calls> |

---

## Deployment

<Keep this concrete — the exact steps that put the project in production.
 Your existing RunFlare notes (managed PostgreSQL, the disk mounted at
 /app/public for static and media, running migrate and collectstatic in the
 start command because the disk mounts at runtime) belong here as they are.
 That level of specificity is exactly what a reviewer wants to see.>

---

## Testing

```bash
pytest
```

<State honestly what is covered and what is not.

 Example: Unit tests cover the prescription refill rules, the order state
 machine and the OTP flow against a dummy notification backend. Template
 rendering and the front end have no automated tests yet.>

---

## Roadmap

- [ ] <Public content pages and launch hardening>
- [ ] <Online payment once e-Namad is issued>
- [ ] <Expose a REST API with Django REST Framework>
- [ ] <Add CI on GitHub Actions to run pytest on every push>

---

## Documentation

- [PLAN.md](PLAN.md) — <scope and phases>
- [CONTEXT.md](CONTEXT.md) — <domain background and constraints>
- [docs/adr/](docs/adr/) — <architecture decision records>

---

## License

<Proprietary — all rights reserved. / MIT.> See [LICENSE](LICENSE).

## Contact

<Ahmad (Aria) Aramesh Moghaddam> — <email> — [github.com/Aramesh-Aria](https://github.com/Aramesh-Aria) — [aria-aramesh.ir](https://aria-aramesh.ir)
