from django.http import QueryDict
from django.db.models import Value as V
from django.db.models.functions import Concat

from typing import Iterable

from apps.cases.models import Case
from apps.classifiers.models import ClaimPersonType


def search(params: QueryDict) -> Iterable[Case]:
    res = Case.objects.select_related('claim', 'claim__obj_kind')

    if params.get('person_type'):
        if params['person_type'] == 'appellant':
            res = res.filter(
                claim__person__title__icontains=params['person_name'],
                claim__person__person_type=ClaimPersonType.objects.get(title='Апелянт')
            )
        elif params['person_type'] == 'represent':
            res = res.filter(
                claim__person__title__icontains=params['person_name'],
                claim__person__person_type=ClaimPersonType.objects.get(title='Представник апелянта')
            )
        elif params['person_type'] == 'collegium_head':
            res = res.annotate(
                full_name=Concat(
                    'collegiummembership__person__last_name',
                    V(' '),
                    'collegiummembership__person__first_name',
                    V(' '),
                    'collegiummembership__person__middle_name'
                )
            )
            res = res.filter(collegiummembership__is_head=True, full_name__icontains=params['person_name'])
        elif params['person_type'] == 'collegium_member':
            res = res.annotate(
                full_name=Concat(
                    'collegiummembership__person__last_name',
                    V(' '),
                    'collegiummembership__person__first_name',
                    V(' '),
                    'collegiummembership__person__middle_name'
                )
            )
            res = res.filter(full_name__icontains=params['person_name'])
        elif params['person_type'] == 'expert':
            res = res.annotate(
                full_name=Concat(
                    'expert__last_name',
                    V(' '),
                    'expert__first_name',
                    V(' '),
                    'expert__middle_name'
                )
            )
            res = res.filter(full_name__icontains=params['person_name'])

    if params.get('case_number'):
        res = res.filter(case_number__icontains=params['case_number'])

    if params.get('obj_number'):
        res = res.filter(claim__obj_number__icontains=params['obj_number'])

    if params.get('obj_title'):
        res = res.filter(claim__obj_title__icontains=params['obj_title'])

    if params.get('case_date_from'):
        res = res.filter(created_at__gte=f"{params['case_date_from']} 00:00:00")

    if params.get('case_date_to'):
        res = res.filter(created_at__lte=f"{params['case_date_to']} 23:59:59")

    if params.get('claim_kind'):
        res = res.filter(claim__claim_kind_id=params['claim_kind'])

    if params.get('refusal_reason'):
        res = res.filter(refusal_reasons__id=params['refusal_reason'])

    if params.get('has_decision'):
        if params['has_decision'] == 'yes':
            res = res.filter(decision_date__isnull=False)
        elif params['has_decision'] == 'no':
            res = res.filter(decision_date__isnull=True)

    if params.get('decision_type'):
        res = res.filter(decision_type_id=params['decision_type'])

    if params.get('history_keywords'):
        res = res.filter(casehistory__action__icontains=params['history_keywords'])

    return res
