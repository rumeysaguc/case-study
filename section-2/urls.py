from django.urls import path

from .views import (
    AssistanceRequestCreateView,
    AssistanceRequestCompleteView,
    AssistanceRequestCancelView,
)

urlpatterns = [
    path("request/", AssistanceRequestCreateView.as_view(), name="assistance-create"),
    path("request/<int:request_id>/complete/", AssistanceRequestCompleteView.as_view(), name="assistance-complete"),
    path("request/<int:request_id>/cancel/", AssistanceRequestCancelView.as_view(), name="assistance-cancel"),
]
