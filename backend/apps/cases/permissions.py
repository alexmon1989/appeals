from rest_framework.permissions import IsAuthenticated

from .services import services


class HasAccessToCase(IsAuthenticated):
    """Проверяет, имеет ли пользователь отношение к апелляционному делу."""
    def has_permission(self, request, view):
        base_res = super().has_permission(request, view)
        return base_res and services.case_user_has_access(view.kwargs['id'], request.user)
