from django.http import QueryDict

from typing import Iterable

from apps.cases.models import Case


def search(params: QueryDict) -> Iterable[Case]:
    res = Case.objects.select_related('claim', 'claim__obj_kind')

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
