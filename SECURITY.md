# Security policy

Only the current main branch is maintained. This is an early MVP and has not received an independent security audit.

Report vulnerabilities privately using the repository's GitHub Security → Report a vulnerability if enabled. If private reporting is unavailable, contact the maintainer via a contact method on their GitHub profile; do not post secrets or exploit details in public issues.

Never commit credentials, `.env`, databases, private grant proposals, personal information, or confidential institutional code. Use synthetic test fixtures. Rotate accidentally exposed credentials immediately and contact the maintainer about history cleanup.

The app uses Django authentication, password validators, CSRF middleware, template escaping and ownership/staff checks. Production defaults require a secret, secure cookies and HTTPS redirects. There are no file uploads or public registration. Operators must provide login rate limits, backups, monitoring, access reviews and timely dependency upgrades. Review docs/DEPLOYMENT.md before using real data.

A dependency audit reports known published advisories at scan time; passing tests and scans is not a security guarantee.
