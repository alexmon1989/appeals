from django.contrib.auth import get_user_model

from ..models import Case

from typing import Iterable

UserModel = get_user_model()


def case_get_list(user: UserModel) -> Iterable[Case]:
    """Возвращает список апелляционных дел, к которым есть доступ у пользователя"""
    cases = Case.objects.select_related('obj_kind', 'claim_kind')
    return cases

