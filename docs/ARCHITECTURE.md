# Architecture

Django renders server-side HTML with a small local CSS file. No external asset services or JavaScript packages are needed. SQLite stores users, sessions, funding calls, applications and final decisions.

- `opengrant/`: environment-based settings, URL configuration and WSGI entry point.
- `grants/models.py`: positive funding constraints, proposal states and one final decision per application.
- `grants/forms.py`: allowlisted editable fields, budget and call validation.
- `grants/views.py`: ownership/staff authorization, POST-only submission, transactions and conditional state changes.
- `grants/admin.py`: call administration and read-only proposal/decision access.
- `grants/tests.py`: workflow, authorization, CSRF, escaping and validation regression tests.

Accounts are provisioned by administrators. Staff status grants broad reviewer access to proposals; there are no departmental scopes. A staff user cannot review their own application. Superusers can manage accounts and calls; database operators remain trusted.

Drafts can only be edited by their owner. Submission locks further edits and revalidates the current funding call. Review accepts submitted applications only, requires feedback, and stores a final immutable-through-the-UI decision. The application status and decision are saved in the same transaction. These are application controls, not tamper-proof audit records.

All project code was authored from scratch for this repository. No external institutional files were imported. The optional sample fund contains fictional text only.
