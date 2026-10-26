from django.contrib import admin
from .models import Application, Decision, GrantCall


@admin.register(GrantCall)
class GrantCallAdmin(admin.ModelAdmin):
    list_display = ["title", "deadline", "max_amount", "currency", "is_open"]
    list_filter = ["is_open"]


class ReadOnlyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Application)
class ApplicationAdmin(ReadOnlyAdmin):
    list_display = ["title", "applicant", "status", "amount"]
    list_filter = ["status"]


@admin.register(Decision)
class DecisionAdmin(ReadOnlyAdmin):
    list_display = ["application", "reviewer", "outcome", "created_at"]
