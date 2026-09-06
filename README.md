# Vet Clinic & Pharmacy

A Farsi, right-to-left Django application for a single mixed-practice veterinary
clinic and pharmacy — public catalogue plus a logged-in client portal for animal
records, orders, prescriptions and appointments. It is one business's site, not a
multi-tenant product.

**Status:** in development, backend-first, pre-launch &nbsp;·&nbsp;
🔗 **Live:** not public yet — deploys to a RunFlare staging host (`vet-pharmecy.runflare.run`) &nbsp;·&nbsp;
📦 **Releases:** none tagged yet &nbsp;·&nbsp;
🧪 **Tests:** 100 pytest tests across 10 apps (domain rules, not templates)

---

## Screenshots

There is no public front end yet. The project is built backend-first: models,
domain services and flows run through the Django admin and server-rendered
templates, and the polished Farsi/RTL front end is designed later (see
[docs/frontend-brief.md](docs/frontend-brief.md)). The [Architecture](#architecture)
section below is the current picture of the system.

---

## Problem

A single local veterinary practice runs both a clinic (consultations,
appointments, visit records) and a pharmacy/store (medications, equipment). It is
a mixed practice — companion pets, ornamental birds, horses and livestock, not
only pets. Orders, prescription refills and appointment requests are handled over
the phone and on paper, so vaccination due-dates are tracked by memory and
refills are frequently missed.

## What I built

A Persian, right-to-left Django application covering the product catalogue
(organised by animal category first), per-animal and per-herd records, cart and
order lifecycle with stock reservation, prescriptions with refill requests,
appointment requests with a staff-confirm flow, visit records and vaccinations
with a due-date reminder job — plus SMS/email notifications behind a pluggable
backend. Deployment is configured on RunFlare (Iranian PaaS) straight from git.
Public content polish and launch hardening (Phase 4) are pending; online payment
and the paid Online Visit (Phase 5) wait on the client obtaining an e-Namad
seal, which itself requires the live site.

**My role:** Sole developer — requirements, domain model, architecture,
implementation, tests and deployment.

---

## Architecture

| App | Responsibility |
|---|---|
| `config` | Split settings (base/dev/prod), URLs, WSGI/ASGI |
| `accounts` | Custom User with phone identity (ADR-0004), OwnerProfile, OTP auth |
| `core` | Base templates, Jalali/Persian template filters |
| `notifications` | `notify()` plus pluggable SMS/email backends; OTP delivery (ADR-0003) |
| `catalog` | AnimalCategory + Section taxonomy, Products, browse/filter (ADR-0006) |
| `animals` | Animal (companion + equine) and Herd (livestock) models, owner-scoped CRUD |
| `pharmacy` | Cart, Order lifecycle, Prescriptions and Refill Requests |
| `appointments` | Appointment request → staff-confirm lifecycle |
| `records` | Visit Records, Vaccinations, due-date reminder command |
| `payments` | Payment model and backend interface; pay-at-pickup (ADR-0005) |
| `pages` | Public home with animal-category tiles |

When an owner requests a prescription refill, the view in `pharmacy` calls a
domain service that validates the prescription against its remaining authorised
quantity and active state, creates a `RefillRequest` in a pending state for staff
to approve, and routes any messaging through `notify()` in `notifications` rather
than an SMS client directly. The delivery backend is chosen from settings, so
switching SMS providers touches one module and no view code. Money is integer
Rial throughout, and stock is decremented when an order is placed and restored on
cancellation so the catalogue cannot oversell.

---

## Key design decisions

| Decision | Why | Trade-off accepted |
|---|---|---|
| Phone number as the user identity instead of email ([ADR-0004](docs/adr/0004-custom-user-phone-identity.md)) | Clients are Iranian owners and farmers who reliably have a mobile number, not an email address | Login depends on an SMS provider being up and costs money per message; custom User model had to land before the first migration |
| Notification layer behind a `notify()` interface with pluggable backends ([ADR-0003](docs/adr/0003-sms-provider-notification-layer.md)) | The SMS provider can be swapped (Iran-reachable only, never Twilio), and tests run against a console backend with no network | One more indirection than calling the SMS client directly |
| Pay at pickup instead of an online gateway in v1 ([ADR-0005](docs/adr/0005-online-payment-iranian-gateway.md)) | A payment gateway requires an e-Namad seal, which requires a live site; the rest of the product ships without it | Orders are not settled in the system; online payment and the paid Online Visit are deferred to Phase 5 |
| Server-rendered templates + HTMX instead of an SPA ([ADR-0001](docs/adr/0001-server-rendered-htmx.md)) | One developer, one small client, SEO-relevant public pages; avoids a separate front-end build and API surface | Rich client-side interactions are more work; no ready-made mobile client |
| Catalogue and navigation organised by animal category first ([ADR-0006](docs/adr/0006-animal-category-information-architecture.md)) | Matches how a mixed-practice clientele thinks (bird owner vs. sheep farmer) and keeps each category's four sections consistent | Products need a category + section even when the split is arbitrary; cross-category browsing is secondary |
| Split settings into base/dev/prod | Same codebase runs on SQLite locally and PostgreSQL in production without edits | Three files to keep in sync instead of one |
| Deployed from git on RunFlare without Docker | Iranian PaaS with the shortest path to a running site for a single small client | Less portable than a container; the environment is defined by the platform, not the repo |

---

## Tech stack

- **Language:** Python 3.11
- **Framework:** Django 5.2
- **Database:** PostgreSQL in production (psycopg 3), SQLite in local development
- **Serving:** Gunicorn + WhiteNoise
- **Deployment:** RunFlare, deployed straight from the git repo (no Docker)
- **Other:** django-environ, Jalali calendar (jdatetime, django-jalali), Pillow;
  ruff + pytest / pytest-django for tooling

---

## Getting started

```bash
git clone https://github.com/Aramesh-Aria/vet-pharmecy.git
cd vet-pharmecy
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env        # then fill in the values
python manage.py migrate
python manage.py createsuperuser   # prompts for phone + password
python manage.py seed_data         # sample categories/products
python manage.py runserver
```

Dev uses SQLite and `config.settings.dev` by default. Run the tests with `pytest`.

**Environment variables**

| Variable | Purpose |
|---|---|
| `DJANGO_SETTINGS_MODULE` | `config.settings.dev` locally, `config.settings.prod` in production |
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` locally, `False` in production |
| `ALLOWED_HOSTS` | comma-separated hostnames (prod defaults include `.runflare.run`) |
| `DATABASE_URL` | PostgreSQL connection string in production; unset falls back to SQLite |
| `SMS_BACKEND` / `SMS_API_KEY` / `SMS_SENDER` | SMS gateway (Kavenegar) in production; console backend in dev |
| `PAYMENTS_BACKEND` / `PAYMENTS_ONLINE_ENABLED` | pay-at-pickup backend now; flip on post-e-Namad for the online gateway |

---

## Deployment

Deployed on RunFlare directly from the git repo — no Docker, no Procfile.

- **Database** — create a managed **PostgreSQL** service (16.2 recommended, not
  PostGIS) and set
  `DATABASE_URL=postgres://USER:PASSWORD@<db-service-name>:5432/DBNAME`. You
  cannot attach a disk to a database service; RunFlare's managed Postgres handles
  its own storage.
- **Disk** — add one disk at path **`/app/public`**. Static and media are served
  from `/public/` per RunFlare's Django docs
  (`STATIC_ROOT=/app/public/static`, `MEDIA_ROOT=/app/public/media`); the disk
  keeps uploaded media across deploys.
- **Start command** — because that disk mounts at **runtime**, run `migrate` and
  `collectstatic` there rather than only at build time:

  ```
  python manage.py migrate --noinput && \
  python manage.py collectstatic --noinput && \
  gunicorn config.wsgi:application --bind 0.0.0.0:8000
  ```

- **Env** — `DJANGO_SETTINGS_MODULE=config.settings.prod`, `DEBUG=False`,
  `SECRET_KEY`, `DATABASE_URL`, `ALLOWED_HOSTS`. `CSRF_TRUSTED_ORIGINS` defaults
  to the HTTPS form of each host (a `.runflare.run` host becomes
  `https://*.runflare.run`). Static uses non-manifest storage (stable filenames)
  so RunFlare serves by path, with WhiteNoise as a compressing fallback; the
  source assets live in `static/` and `public/` is generated (gitignored).
- **After the first deploy** — create a superuser and run
  `python manage.py seed_data` from the RunFlare console.

### Scheduled jobs

`python manage.py send_vaccination_reminders [--days N]` — notify owners of
vaccinations coming due. Run from cron (e.g. daily) per PLAN §4.

---

## Testing

```bash
pytest
```

Tests cover the domain rules: the cart and order lifecycle with stock
reservation, prescription and refill-request validation, the appointment
state flow, catalogue taxonomy and browsing, the payment backend interface, the
OTP/auth flow, and vaccination reminders — all against a console notification
backend with no network. Template rendering and the (not-yet-built) front end
have no automated tests.

---

## Roadmap

- [ ] Phase 4 — public content pages, business-identity/terms pages (needed for
  e-Namad), SEO, RTL/accessibility QA, launch hardening → **first live deploy (payment-less)**
- [ ] Milestone — obtain e-Namad (نماد الکترونیک) with the live site
- [ ] Phase 5 — online payment via an Iranian gateway (Zarinpal), switch orders
  to pay-online-before-pickup, build the paid Online Visit
- [ ] Add CI on GitHub Actions to run pytest + ruff on every push
- [ ] Phase 6 — vet-team bios, pet-care articles

---

## Documentation

- [PLAN.md](PLAN.md) — scope, information architecture and build phases
- [CONTEXT.md](CONTEXT.md) — domain background, constraints and the project glossary
- [docs/adr/](docs/adr/) — architecture decision records
- [docs/frontend-brief.md](docs/frontend-brief.md) — brief for the later front-end design

---

## License

Proprietary — all rights reserved.

## Contact

Aria Aramesh — aramesh_aria@yahoo.com — [github.com/Aramesh-Aria](https://github.com/Aramesh-Aria) — [aria-aramesh.ir](https://aria-aramesh.ir)
