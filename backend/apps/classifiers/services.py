from .models import ObjKind, ClaimKind

from typing import List


def get_obj_kinds_list() -> List[ObjKind]:
    """Возвращает список типов об-ов инт. собств."""
    return list(ObjKind.objects.order_by('pk').values('pk', 'title', 'sis_id'))


def get_claim_kinds(bool_as_int: bool = False) -> List[ClaimKind]:
    """Возвращает список видов обращений."""
    claim_kinds = list(ClaimKind.objects.order_by('pk').values('pk', 'title', 'obj_kind_id', 'third_person'))
    if bool_as_int:
        for claim_kind in claim_kinds:
            claim_kind['third_person'] = int(claim_kind['third_person'])
    return claim_kinds
