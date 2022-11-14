from .models import Absence, Meeting, Invitation

from django.utils import timezone
from django.db.models import Q, QuerySet

from datetime import timedelta, date, datetime
from typing import Iterable, List


def invitation_get_list_qs(user_id: int) -> QuerySet[Invitation]:
    """Возвращает список будущих неподтверждённых и неотвергнутых приглашений пользователя."""
    res = Invitation.objects.select_related(
        'meeting', 'meeting__case'
    ).filter(
        user_id=user_id,
        meeting__datetime__gte=timezone.now(),
        meeting__meeting_type='COMMON',
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
    if invitation and invitation.meeting.case.stage_step.code == 3001:
        invitation.accepted_at = None
        invitation.rejected_at = timezone.now()
        invitation.save()
        return True
    return False


def invitation_create_collegium_invitations(meeting_id: int) -> None:
    """Создаёт приглашения к участию в заседании членов коллегии."""
    meeting = Meeting.objects.prefetch_related(
        'case__collegiummembership_set__person'
    ).filter(
        pk=meeting_id
    ).first()

    if meeting:
        for item in meeting.case.collegiummembership_set.all():
            Invitation.objects.create(
                user_id=item.person.pk,
                meeting_id=meeting_id
            )
        # Секретарь
        invitation, created = Invitation.objects.get_or_create(
            user_id=meeting.case.secretary_id,
            meeting_id=meeting.pk,
        )
        if created:
            invitation.accepted_at = timezone.now()
            invitation.save()


def invitation_get_one(pk: int) -> Invitation:
    """Возвращает приглошение."""
    return Invitation.objects.filter(pk=pk).first()


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


def absence_get_users_periods(users_ids: Iterable[int]) -> List[dict]:
    """Возвращает список периодами, когда пользователи users_ids отсутствуют."""
    res = {}

    date_now = timezone.now().date()
    absences = Absence.objects.filter(
        Q(user_id__in=users_ids),
        Q(date_from__gte=date_now) | Q(date_from__lte=date_now, date_to__gte=date_now)
    ).select_related('user')

    for absence in absences:
        item = {
            'date_from': absence.date_from,
            'date_to': absence.date_to,
        }
        if absence.user.get_full_name in res:
            res[absence.user.get_full_name].append(item)
        else:
            res[absence.user.get_full_name] = [item]

    return [{'name': key, 'periods': res[key]} for key in res.keys()]


def absence_users_present_on_date(date_check: date, users_ids: Iterable[int]) -> bool:
    """Проверяет не отсутствуют ли сотрудники на конкретную дату."""
    return not Absence.objects.filter(
        user_id__in=users_ids, date_from__lte=date_check, date_to__gte=date_check
    ).exists()


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


def meeting_create_pre_meeting(meeting_datetime: datetime, case_id: int) -> Meeting:
    """Создание предварительного заседания."""
    meeting = Meeting.objects.create(
        meeting_type=Meeting.MeetingTypeChoices.PRE,
        datetime=meeting_datetime,
        case_id=case_id
    )

    # Создание приглашений (принятых)
    accepted_at = timezone.now()
    for item in meeting.case.collegiummembership_set.all():
        Invitation.objects.create(
            user_id=item.person.pk,
            meeting_id=meeting.pk,
            accepted_at=accepted_at
        )
    Invitation.objects.get_or_create(
        user_id=meeting.case.secretary_id,
        meeting_id=meeting.pk,
        accepted_at=accepted_at
    )

    return meeting
