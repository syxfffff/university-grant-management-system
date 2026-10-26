from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("calls/<int:call_id>/apply/", views.create, name="create"),
    path("applications/<int:pk>/", views.detail, name="detail"),
    path("applications/<int:pk>/edit/", views.edit, name="edit"),
    path("applications/<int:pk>/submit/", views.submit, name="submit"),
    path("reviews/", views.review_queue, name="queue"),
    path("reviews/<int:pk>/", views.review, name="review"),
]
