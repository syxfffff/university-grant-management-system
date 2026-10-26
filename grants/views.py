from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from .forms import ApplicationForm, DecisionForm
from .models import Application, Decision, GrantCall


@login_required
def dashboard(request):
    applications = Application.objects.filter(applicant=request.user).select_related("call")
    calls = GrantCall.objects.filter(is_open=True, deadline__gte=timezone.localdate())
    return render(request, "grants/dashboard.html", {"applications": applications, "calls": calls})


@login_required
def create(request, call_id):
    call = get_object_or_404(GrantCall, pk=call_id, is_open=True, deadline__gte=timezone.localdate())
    application = Application(applicant=request.user, call=call)
    form = ApplicationForm(request.POST or None, instance=application)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Draft saved. Review it before submitting.")
        return redirect("detail", pk=application.pk)
    return render(request, "grants/form.html", {"form": form, "call": call})


@login_required
def detail(request, pk):
    application = get_object_or_404(Application.objects.select_related("call", "applicant"), pk=pk)
    if application.applicant_id != request.user.pk and not request.user.is_staff:
        raise PermissionDenied
    decision = Decision.objects.filter(application=application).first()
    return render(request, "grants/detail.html", {"application": application, "decision": decision})


@login_required
@transaction.atomic
def edit(request, pk):
    application = get_object_or_404(Application.objects.select_for_update(), pk=pk, applicant=request.user, status=Application.Status.DRAFT)
    form = ApplicationForm(request.POST or None, instance=application)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("detail", pk=pk)
    return render(request, "grants/form.html", {"form": form, "call": application.call})


@login_required
@require_POST
@transaction.atomic
def submit(request, pk):
    application = get_object_or_404(Application.objects.select_for_update(), pk=pk, applicant=request.user, status=Application.Status.DRAFT)
    form = ApplicationForm({"title": application.title, "abstract": application.abstract, "amount": application.amount}, instance=application)
    if not form.is_valid():
        return HttpResponseBadRequest("The call is closed or the application is invalid. Edit your draft or contact an administrator.")
    changed = Application.objects.filter(pk=pk, status=Application.Status.DRAFT).update(status=Application.Status.SUBMITTED, updated_at=timezone.now())
    if changed != 1:
        return HttpResponseBadRequest("This application has already changed.")
    messages.success(request, "Application submitted.")
    return redirect("detail", pk=pk)


@login_required
def review_queue(request):
    if not request.user.is_staff:
        raise PermissionDenied
    applications = Application.objects.filter(status=Application.Status.SUBMITTED).exclude(applicant=request.user).select_related("applicant", "call")
    return render(request, "grants/queue.html", {"applications": applications})


@login_required
@transaction.atomic
def review(request, pk):
    if not request.user.is_staff:
        raise PermissionDenied
    application = get_object_or_404(Application.objects.select_for_update(), pk=pk, status=Application.Status.SUBMITTED)
    if application.applicant_id == request.user.pk:
        raise PermissionDenied("You cannot review your own application.")
    form = DecisionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        decision = form.save(commit=False)
        decision.application = application
        decision.reviewer = request.user
        changed = Application.objects.filter(pk=pk, status=Application.Status.SUBMITTED).update(status=decision.outcome, updated_at=timezone.now())
        if changed != 1:
            return HttpResponseBadRequest("This application has already been reviewed.")
        decision.save()
        messages.success(request, "Decision recorded.")
        return redirect("detail", pk=pk)
    return render(request, "grants/review.html", {"application": application, "form": form})
