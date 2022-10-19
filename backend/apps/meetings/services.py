from .models import Absence, Meeting, Invitation

from django.utils import timezone
from django.db.models import Q, QuerySet

from datetime import timedelta


def invitation_get_list_qs(user_id: int) -> QuerySet[Invitation]:
    """Возвращает список будущих неподтверждённых и неотвергнутых приглашений пользователя."""
    res = Invitation.objects.select_related(
        'meeting', 'meeting__case'
    ).filter(
        user_id=user_id,
        meeting__datetime__gte=timezone.now()
    ).order_by('-meeting__datetime')
    return res


def invitation_accept(pk: int, user_id: int) -> bool:
    """Принимает приглашение к участию в заседании."""
    invitation = Invitation.objects.filter(pk=pk, user_id=user_id).first()
    if invitation:
        invitation.accepted_at = timezone.now()
        invitation.rejected_at = None
        invitation.save()
        return True
    return False


def invitation_reject(pk: int, user_id: int) -> bool:
    """Отклоняет приглашение к участию в заседании."""
    invitation = Invitation.objects.filter(pk=pk, user_id=user_id).first()
    # Отменять можно только если не сформировано оповещение апеллянту
    if invitation and invitation.meeting.case.stage_step.code == 3000:
        invitation.accepted_at = None
        invitation.rejected_at = timezone.now()
        invitation.save()
        return True
    return False


def absence_get_all_qs(user_id: int) -> QuerySet[Absence]:
    """Возвращает список настоящих или будущих периодов отсутствия сотрудника на работе."""
    res = Absence.objects.filter(
        user_id=user_id,
        date_to__gte=timezone.now()
    )
    return res


def absence_get_calendar_events(user_id: int, start: str, end: str) -> list:
    """Возвращает список событий для календаря."""
    items = Absence.objects.filter(
        user_id=user_id,
        date_to__gte=start,
        date_from__lte=end
    )
    res = []
    for item in items:
        item_end = item.date_to + timedelta(days=1)
        res.append({
            "id": f"absence_{item.pk}",
            "title": "Період відсутності",
            "description": "",
            "start": item.date_from.strftime('%Y-%m-%d'),
            "end": item_end.strftime('%Y-%m-%d'),
            "className": "bg-warning border-warning text-dark"
        })
    return res


def absense_get_one(pk: int, user_id: int) -> Meeting:
    """Получает данные периода отсутствия пользователя."""
    return Absence.objects.filter(pk=pk, user_id=user_id).first()


def absense_delete_one(pk: int, user_id: int) -> tuple:
    """Удаляет данные периода отсутствия пользователя."""
    return Absence.objects.filter(pk=pk, user_id=user_id).delete()


def meeting_get_calendar_events(user_id: int, start: str, end: str):
    """Возвращает список событий для календаря."""
    meetings = Meeting.objects.select_related('case').filter(
        invitation__user_id=user_id,
        datetime__gte=start,
        datetime__lte=end
    ).exclude(
        # отказ или не подтверждено
        Q(invitation__rejected_at__isnull=False) | Q(invitation__accepted_at__isnull=True)
    )
    res = []
    for item in meetings:
        res.append({
            "id": f"meeting_{item.pk}",
            "title": item.case.case_number,
            "description": "",
            "start": item.datetime.strftime('%Y-%m-%dT%H:%M:%S'),
            "className": "bg-primary border-primary"
        })
    return res


def meeting_get_one(pk: int, user_id: int) -> Meeting:
    """Получает данные заседания, в котором участвует пользователь."""
    return Meeting.objects.select_related('case').filter(pk=pk, invitation__user_id=user_id).first()
