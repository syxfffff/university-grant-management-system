# Deployment

This repository ships an MVP application, not hosted infrastructure. Use Python 3.12/3.13 and install `requirements.txt` in an isolated environment.

1. Generate a secret with `python -c 'import secrets; print(secrets.token_urlsafe(64))'`. Store it as `DJANGO_SECRET_KEY` in your host's secret manager, never Git.
2. Set `DJANGO_DEBUG=false` and `DJANGO_ALLOWED_HOSTS=your.actual.domain`. Do not use wildcard hosts. Configure `DJANGO_DB_PATH` to a persistent, access-restricted SQLite location outside the source checkout.
3. Run `python manage.py migrate`, `python manage.py collectstatic --noinput`, and `python manage.py createsuperuser`. Create individual accounts, not shared credentials.
4. Install a maintained WSGI server separately, such as Gunicorn. Serve `opengrant.wsgi:application` behind HTTPS. The development `runserver` is not a production server. Serve `staticfiles/` at `/static/` through your web server; do not expose the database or source directory.
5. Terminate TLS at a trusted proxy. If the application receives plain HTTP behind that proxy, configure Django `SECURE_PROXY_SSL_HEADER` in deployment-specific settings **only after** the proxy strips incoming forwarded headers and sets its own. Without correct proxy configuration, HTTPS redirects may loop. Never trust arbitrary client-supplied proxy headers.
6. Run `python manage.py check --deploy --fail-level WARNING` with production settings and verify HTTPS, login, cookies, static assets and CSRF in the deployed environment.
7. Add login throttling at the reverse proxy or identity provider before public access. Django does not provide brute-force throttling here. Use network restrictions for admin, monitoring, dependency patching and encrypted backups. Test restoration; database exports contain personal and proposal data.
8. Review access, retention, legal requirements and institution policy before collecting real data. This application is independent of any university.

HSTS includes subdomains and preload by default in production; configure these settings to match the domains you control before exposing the site. Keep DEBUG off for deployments.

SQLite limits concurrent writes and may return a lock error under contention. State changes are conditional and transactional, but this MVP is not load tested. For larger deployments configure PostgreSQL, add its driver, and test concurrent workflows and operational recovery. No containers or one-click deployment are claimed.
