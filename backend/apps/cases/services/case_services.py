from django.contrib.auth import get_user_model
from django.db.models import Count, Q, QuerySet, Prefetch

from ..models import Case, Document, CaseStage, CaseStageStep, CaseHistory, CollegiumMembership, Sign
from ...filling import services as filling_services
from .create_document_service import CollegiumDocumentCreatorService
from .document_services import document_set_reg_number, document_set_barcode

from typing import Iterable, List, Union
import datetime

UserModel = get_user_model()


def case_get_all_qs(order_by: str = '-created_at') -> QuerySet[Case]:
    """Возвращает список апелляционных дел, к которым есть доступ у пользователя"""
    cases = Case.objects.select_related(
        'claim',
        'claim__obj_kind',
        'claim__claim_kind',
        'papers_owner',
        'expert',
        'secretary',
        'stage_step',
        'stage_step__stage',
    ).prefetch_related(
        'collegiummembership_set__person',
        'document_set',
        'document_set__document_type',
        'document_set__sign_set',
        'refusal_reasons'
    ).order_by(order_by)

    return cases


def case_filter_dt_list(cases: QuerySet[Case], current_user_id: int, user: str = None, obj_kind: int = None,
                        stage: str = None) -> Iterable[Case]:
    """Фильтрует список ап. дел по определённым параметрам."""

    # Оставляет только ап. дела, к которым имеет отношение пользователь
    if user and user == 'me':
        current_user = UserModel.objects.get(pk=current_user_id)
        cases = cases.filter(
            Q(collegiummembership__person=current_user)
            | Q(expert=current_user)
            | Q(secretary=current_user)
            | Q(papers_owner=current_user)
        )

    # Фильтр по типу ОИС
    if obj_kind and obj_kind != 'all':
        cases = cases.filter(claim__obj_kind__id=obj_kind)

    if stage and stage != 'all':
        if stage == 'new':
            cases = cases.filter(stage_step__code=1000)
        else:
            cases = cases.filter(stage_step__code__gt=1000)

    return cases


def case_get_documents_qs(case_id: int) -> Iterable[Document]:
    """Возвращает документы дела."""
    claim_id = Case.objects.get(pk=case_id).claim_id
    queryset = Document.objects.filter(
        Q(case_id=case_id) | Q(claim_id=claim_id)
    ).select_related(
        'document_type',
        'case',
        'claim',
        'claim__user',
    ).prefetch_related(
        Prefetch('sign_set', queryset=Sign.objects.all())
    ).annotate(
        signs_count=Count('sign', filter=~Q(sign__timestamp=''))
    ).order_by('-created_at')

    return queryset


def case_generate_next_number() -> str:
    """Генерирует следующий номер дела."""
    cur_year = datetime.datetime.now().year
    last_case = Case.objects.filter(created_at__year=cur_year).order_by('-created_at').first()
    if last_case:
        last_case_num = last_case.case_number.split('/')[0]
        last_case_num = str(int(last_case_num) + 1).zfill(4)
        return f"{last_case_num}/{cur_year}"
    else:
        return f"0001/{cur_year}"


def case_create_from_claim(claim_id: int, user: UserModel) -> Union[Case, None]:
    """Создаёт дело на основе обращения."""
    claim = filling_services.claim_get_user_claims_qs(user).filter(pk=claim_id, status=2).first()
    if claim:
        case = Case.objects.create(
            claim=claim,
            case_number=case_generate_next_number(),
            stage_step=CaseStageStep.objects.get(code=1000)
        )
        claim.status = 3
        claim.submission_date = datetime.datetime.now()
        claim.save()

        # Присваивание документам номеров и штрихкодов
        for doc in claim.document_set.all():
            document_set_reg_number(doc.pk)
            document_set_barcode(doc.pk)

        return case
    return None


def case_get_stages(case_id: int) -> Union[List[dict], None]:
    """Возвращает стадии ап. дела."""
    case = case_get_all_qs().filter(pk=case_id).first()
    if case:
        stages = CaseStage.objects.order_by('number')
        res = []
        current_stage_step = case.stage_step
        for stage in stages:
            if current_stage_step.stage.number > stage.number:
                status = 'done'
            elif current_stage_step.stage.number == stage.number:
                if current_stage_step.case_stopped:
                    status = 'done'
                else:
                    status = 'current'
            else:
                status = 'not-active'

            res.append({
                'title': stage.title,
                'number': stage.number,
                'status': status
            })
        return res
    return None


def case_add_history_action(case_id: int, action: str, user_id: int) -> None:
    """Добавляет действие в историю действий дела."""
    CaseHistory.objects.create(
        case_id=case_id,
        action=action,
        user_id=user_id
    )


def case_take_to_work(case_id: int, user_id: int) -> bool:
    """Принимает дело в работу (назначает секретаря и меняет статус на 2000)."""
    case = Case.objects.filter(pk=case_id, stage_step__code=1000).first()
    if case:
        case.secretary_id = user_id
        case.save()
        case_change_stage_step(case_id, 2000, user_id)
        return True
    return False


def case_change_stage_step(case_id: int, stage_step_code: int, user_id: int) -> None:
    """Присваивает делу новую стадию и делает отметку в журнале дела."""
    case = Case.objects.get(pk=case_id)
    stage_step = CaseStageStep.objects.get(code=stage_step_code)
    case.stage_step = stage_step
    case.save()
    case_add_history_action(
        case_id,
        f'Зміна стадії справи на "{stage_step.title}" (код {stage_step.code})',
        user_id
    )


def case_get_history(case_id: int):
    """Возвращает историю действий по ап. делу."""
    return CaseHistory.objects.filter(
        case_id=case_id
    ).select_related(
        'user',
    ).order_by(
        '-created_at'
    )


def case_create_collegium(case_id: int, head_id: int, members_ids: List[int], signer_id: int, user_id: int) -> None:
    """Создаёт коллегию для рассмотрения дела."""
    # Создание коллегии в БД
    CollegiumMembership.objects.create(
        person_id=head_id,
        case_id=case_id,
        is_head=True
    )
    for member_id in members_ids:
        CollegiumMembership.objects.create(
            person_id=member_id,
            case_id=case_id,
            is_head=False
        )

    # Создание документа распоряжения
    service = CollegiumDocumentCreatorService()
    document = service.execute(case_id=case_id, signer_id=signer_id)

    # Подписант
    Sign.objects.create(
        document=document,
        user_id=signer_id,
    )

    # Запись в историю дела
    case_add_history_action(
        case_id,
        'Створено колегію для розгляду справи.',
        user_id
    )

    # Смена статуса дела
    case_change_stage_step(case_id, 2002, user_id)