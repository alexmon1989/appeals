from rest_framework.permissions import IsAuthenticated


class HasAccessToCase(IsAuthenticated):
    """Проверяет, имеет ли пользователь доступ к апелляционному делу."""
    def has_permission(self, request, view):
        base_res = super().has_permission(request, view)
        return base_res and request.user.is_internal
