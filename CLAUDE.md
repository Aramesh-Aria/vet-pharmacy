# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Farsi-first, RTL Django 5.2 site for **one** mixed-practice vet clinic + pharmacy (not multi-tenant). Public catalogue plus a logged-in Owner portal; Staff work through the Django admin. Python 3.11.

Also read `agents.md`: shared skills live in `~/ai-skills/skills`. Before starting, check whether one applies (preferred: tdd, diagnose, grill-with-docs, zoom-out, codebase-design, improve-codebase-architecture, to-prd) and follow it.

## Commands

```bash
source .venv/bin/activate
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py runserver            # settings default to config.settings.dev (SQLite at database/db.sqlite3)
python manage.py seed_data            # sample categories/products
python manage.py send_vaccination_reminders [--days N]   # cron job

pytest                                         # full suite (pytest.ini sets DJANGO_SETTINGS_MODULE)
pytest apps/pharmacy/tests.py                  # one file
pytest apps/pharmacy/tests.py::SomeTest::test_x  # one test
pytest -k refill                               # by keyword
ruff check .
python manage.py makemigrations --check --dry-run
```

Test files match `tests.py`, `tests_*.py`, `test_*.py`. In the sandbox, curl to a local runserver needs `--noproxy '*'`.

## Layout and conventions

- All Django apps live under `apps/` as `apps.<name>` packages: accounts, core, notifications, catalog, animals, pharmacy, appointments, records, payments, pages. App **labels** stay the bare name (`accounts`, `core`, …), so model refs and migrations use `"accounts.User"` and `("accounts", "0001_initial")`. Python imports and dotted paths use `apps.<name>...`.
- `config/settings/{base,dev,prod}.py` are split settings read via django-environ from `.env`.
- Project templates are in `templates/<app>/`, and static source in `static/`. `public/` (collected static + media) and `database/` are generated and gitignored.
- Business logic lives in each app's `services.py` (domain services). Views stay thin and call those services. Lifecycle states are `TextChoices` `Status` enums on the models.
- Money is integer Rial everywhere. Stock is decremented when an order is placed and restored when it is cancelled.
- UI strings and error messages are in Farsi. Dates are Jalali (`django_jalali`, `apps/core/templatetags/persian.py`).

## Cross-cutting architecture

- **Identity (ADR-0004):** the custom `accounts.User` uses the phone number as the login identity, with OTP verification/reset in `apps/accounts/otp.py`. Roles: Owner vs Staff.
- **Notifications (ADR-0003):** always go through `apps.notifications.service.notify(owner, event, **ctx)`. Events are defined in `notifications/events.py`. Never call an SMS client directly. The SMS backend is `import_string(settings.SMS_BACKEND)`: console in dev, Kavenegar in prod (Iran-reachable providers only, never Twilio). Tests use `@override_settings(SMS_BACKEND="apps.notifications.backends.locmem.LocMemSMSBackend")`. `notify()` logs SMS failures and does not raise them. OTP sends via `send_sms` and does surface failures.
- **Payments (ADR-0005):** a pluggable backend interface in `apps/payments/backends/`. At launch everything is pay-at-pickup (`ManualPickupBackend`). `PAYMENTS_ONLINE_ENABLED` switches checkout to `PAYMENTS_ONLINE_BACKEND` (Zarinpal), gated until the client has its e-Namad. Each `Payment` stores its backend path.
- **Admin:** `apps.core.admin_apps.VetAdminConfig` replaces `django.contrib.admin` and installs `apps.core.admin_site.VetAdminSite`. That site adds a staff dashboard (pending appointments, orders, refills, vaccinations due) and enriched autocomplete.
- **Information architecture (ADR-0006):** the catalogue and navigation are organised by Animal Category first, then by the four Sections (Online Visit, Medication, Equipment, Service).
- **Frontend (ADR-0001):** server-rendered templates plus HTMX, no SPA. The polished front end comes later (`docs/frontend-brief.md`).

Use the glossary in `CONTEXT.md` for domain terms. Say Owner (not client/user), Animal (not pet/patient), Herd (livestock is tracked as a group, never per head), Order (not cart, which is only the pre-checkout draft), Refill Request, Visit Record, and Online Visit (not consultation). Scope and phases are in `PLAN.md`. ADRs are in `docs/adr/`.

## Deployment (RunFlare, from git, no Docker)

- Uses `config.settings.prod` with PostgreSQL via `DATABASE_URL`.
- A disk is mounted at `/app/public`. Static and media are served from `/public/static/` and `/public/media/`, so `migrate` and `collectstatic` run in the start command before `gunicorn config.wsgi:application`.
- TLS is terminated at the edge, so `SECURE_SSL_REDIRECT` must stay off. Turning it on causes a redirect loop.
- Static storage is non-manifest so filenames stay stable.
- Env vars that hold dotted backend paths (`SMS_BACKEND`, `PAYMENTS_BACKEND`, `PAYMENTS_ONLINE_BACKEND`) must use the `apps.` prefix.
