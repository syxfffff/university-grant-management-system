# OpenGrant

An independent, open source university research grant workflow built from scratch with Django and SQLite. This repository is an **MVP**, not an institution's production system. It contains no institutional source code, real grant records, or personal data. The optional sample call is fictional. It is not affiliated with or endorsed by any university.

## Features

- Administrator-managed user accounts and funding calls.
- Researchers create and edit drafts, validate requested budgets, and submit before the deadline.
- Staff review submitted proposals and record an approval or rejection with required feedback.
- Owners can see their own proposals and feedback; other researchers cannot access them.
- No self-review, no editing after submission, and no second decision.
- Django session authentication, CSRF protection, escaped output, password validation and secure production defaults.
- Tests, database migrations, CI and dependency update configuration included.

## Run locally

Requires Python 3.12 or 3.13. No Node.js build is needed.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export DJANGO_DEBUG=true
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver
```

Open http://127.0.0.1:8000 and sign in with your newly created account. Create researcher accounts in `/admin/` → Users. Leave **staff status** off for researchers. Give reviewers **staff status**, but no admin model permissions unless they also administer calls/users. Superusers manage funding calls in `/admin/` → Grant calls. Call amounts use two decimal places; the default currency is MYR. Currency conversion is not supported.

No default usernames or passwords are shipped. For a password reset, the administrator can use the user change form in Django admin or `python manage.py changepassword USERNAME`. There is no public sign-up or email reset service.

`.env.example` documents variables; Django does not automatically load `.env`. Export them in your shell or configure them through your host.

## Workflow and roles

`Draft → Submitted → Approved / Rejected`

Researchers own applications. Staff can view all applications and review submitted applications belonging to other users. Feedback becomes visible to the owner after a decision. The decision and reviewer are preserved as a database record; there is no full audit log of draft edits or call changes. Admin views for applications/decisions are read-only so the normal workflow is used for decisions.

Submission rechecks the call deadline and current budget limit. Deadlines include the entire stated date in UTC. SQLite is for local demonstrations or small single-instance pilots; write concurrency is limited. Move to PostgreSQL and test simultaneous submissions/reviews before a multi-instance deployment.

## Verify

```sh
export DJANGO_DEBUG=true
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test --verbosity 2
python manage.py collectstatic --noinput
python -m pip install pip-audit==2.10.1 ruff==0.14.2
ruff check .
python -m pip_audit -r requirements.txt
```

CI runs these checks on Python 3.12 and 3.13 and checks production security settings. `collectstatic` prepares static assets; this Django project does not require a frontend compilation step.

## Deployment and limitations

See [deployment](docs/DEPLOYMENT.md), [security policy](SECURITY.md), [architecture](docs/ARCHITECTURE.md) and [contributing](CONTRIBUTING.md). Publishing this repository does **not** deploy a public application.

This version has no file uploads, expenditure tracking, disbursements, milestones, email notifications, SSO, multi-tenancy, reviewer assignment, scoring panels, appeals, or full audit logging. It does not implement university-specific policy. Complete a deployment/security review and backup recovery exercise before using real data.

## License

MIT. See [LICENSE](LICENSE). Contributions must be original or appropriately licensed and must not include confidential institutional material.
