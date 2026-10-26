from datetime import timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Application, Decision, GrantCall


class WorkflowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.owner = User.objects.create_user("researcher", password="test-only-password-47")
        cls.other = User.objects.create_user("other", password="test-only-password-48")
        cls.reviewer = User.objects.create_user("reviewer", password="test-only-password-49", is_staff=True)
        cls.call = GrantCall.objects.create(title="Fictional fund", description="Example only", deadline=timezone.localdate() + timedelta(days=10), max_amount=1000)
        cls.application = Application.objects.create(applicant=cls.owner, call=cls.call, title="Synthetic proposal", abstract="Fictional study", amount=100)

    def setUp(self):
        self.client.force_login(self.owner)

    def submit(self):
        return self.client.post(reverse("submit", args=[self.application.pk]))

    def review(self, **data):
        self.client.force_login(self.reviewer)
        return self.client.post(reverse("review", args=[self.application.pk]), data or {"outcome": "approved", "feedback": "Eligible fictional project."})

    def test_login_required(self):
        self.client.logout()
        self.assertRedirects(self.client.get("/"), "/accounts/login/?next=/", fetch_redirect_response=False)

    def test_login_page(self):
        self.client.logout()
        self.assertContains(self.client.get("/accounts/login/"), "Sign in")

    def test_dashboard_and_detail(self):
        self.assertContains(self.client.get("/"), self.application.title)
        self.assertContains(self.client.get(reverse("detail", args=[self.application.pk])), "Synthetic proposal")

    def test_create_and_edit_draft(self):
        response = self.client.post(reverse("create", args=[self.call.pk]), {"title": "New idea", "abstract": "Example", "amount": "500"})
        self.assertEqual(response.status_code, 302)
        created = Application.objects.get(title="New idea")
        self.assertEqual(created.applicant, self.owner)
        response = self.client.post(reverse("edit", args=[created.pk]), {"title": "Updated idea", "abstract": "Example", "amount": "600"})
        self.assertEqual(response.status_code, 302)
        created.refresh_from_db()
        self.assertEqual(created.amount, Decimal("600"))

    def test_status_and_owner_cannot_be_injected(self):
        self.client.post(reverse("create", args=[self.call.pk]), {"title": "Injection", "abstract": "Example", "amount": "500", "status": "approved", "applicant": self.other.pk})
        created = Application.objects.get(title="Injection")
        self.assertEqual(created.status, "draft")
        self.assertEqual(created.applicant, self.owner)

    def test_over_budget_and_nonpositive_amount_rejected(self):
        for amount in ["1001", "0", "-10", "NaN"]:
            response = self.client.post(reverse("create", args=[self.call.pk]), {"title": "Invalid", "abstract": "Example", "amount": amount})
            self.assertEqual(response.status_code, 200)
        self.assertFalse(Application.objects.filter(title="Invalid").exists())

    def test_others_cannot_read_edit_or_submit(self):
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse("detail", args=[self.application.pk])).status_code, 403)
        self.assertEqual(self.client.post(reverse("edit", args=[self.application.pk]), {}).status_code, 404)
        self.assertEqual(self.submit().status_code, 404)

    def test_dashboard_hides_others(self):
        self.client.force_login(self.other)
        self.assertNotContains(self.client.get("/"), "Synthetic proposal")

    def test_submit_locks_draft(self):
        self.assertEqual(self.submit().status_code, 302)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, "submitted")
        self.assertEqual(self.client.post(reverse("edit", args=[self.application.pk]), {}).status_code, 404)
        self.assertEqual(self.submit().status_code, 404)

    def test_submit_requires_post(self):
        self.assertEqual(self.client.get(reverse("submit", args=[self.application.pk])).status_code, 405)

    def test_closed_and_expired_call_block_submission(self):
        self.call.is_open = False
        self.call.save()
        self.assertEqual(self.submit().status_code, 400)
        self.call.is_open = True
        self.call.deadline = timezone.localdate() - timedelta(days=1)
        self.call.save()
        self.assertEqual(self.submit().status_code, 400)
        self.assertEqual(self.client.get(reverse("create", args=[self.call.pk])).status_code, 404)

    def test_changed_budget_revalidated_at_submission(self):
        self.call.max_amount = 50
        self.call.save()
        self.assertEqual(self.submit().status_code, 400)

    def test_nonstaff_cannot_review(self):
        self.assertEqual(self.client.get("/reviews/").status_code, 403)
        self.assertEqual(self.client.post(reverse("review", args=[self.application.pk]), {}).status_code, 403)

    def test_draft_cannot_be_reviewed(self):
        self.assertEqual(self.review().status_code, 404)

    def test_self_review_denied(self):
        self.submit()
        self.owner.is_staff = True
        self.owner.save()
        self.assertEqual(self.client.post(reverse("review", args=[self.application.pk]), {"outcome": "approved", "feedback": "Self"}).status_code, 403)

    def test_approve_and_prevent_second_decision(self):
        self.submit()
        self.assertEqual(self.review().status_code, 302)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, "approved")
        self.assertEqual(Decision.objects.get().reviewer, self.reviewer)
        self.assertEqual(self.review().status_code, 404)
        self.assertEqual(Decision.objects.count(), 1)

    def test_reject(self):
        self.submit()
        self.assertEqual(self.review(outcome="rejected", feedback="Not eligible.").status_code, 302)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, "rejected")

    def test_invalid_decision_and_missing_feedback(self):
        self.submit()
        for data in [{"outcome": "draft", "feedback": "Bad"}, {"outcome": "approved", "feedback": ""}]:
            self.assertEqual(self.review(**data).status_code, 200)
        self.assertFalse(Decision.objects.exists())

    def test_review_queue_and_feedback(self):
        self.submit()
        self.client.force_login(self.reviewer)
        self.assertContains(self.client.get("/reviews/"), "Synthetic proposal")
        self.review()
        self.client.force_login(self.owner)
        self.assertContains(self.client.get(reverse("detail", args=[self.application.pk])), "Eligible fictional project.")

    def test_csrf_enforced(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        self.assertEqual(client.post(reverse("submit", args=[self.application.pk])).status_code, 403)

    def test_html_escaped(self):
        self.application.abstract = "<script>alert(1)</script>"
        self.application.save()
        response = self.client.get(reverse("detail", args=[self.application.pk]))
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, "<script>")

    def test_logout_requires_post(self):
        self.assertEqual(self.client.get("/accounts/logout/").status_code, 405)

    def test_admin_cannot_mutate_applications(self):
        from django.contrib import admin
        from django.test import RequestFactory

        request = RequestFactory().get("/admin/")
        request.user = self.reviewer
        for model in [Application, Decision]:
            model_admin = admin.site._registry[model]
            self.assertFalse(model_admin.has_add_permission(request))
            self.assertFalse(model_admin.has_change_permission(request))
            self.assertFalse(model_admin.has_delete_permission(request))
