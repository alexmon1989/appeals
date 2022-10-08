from .models import ObjKind, ClaimKind, DocumentType

from typing import List, Type


def get_obj_kinds_list() -> List[dict]:
    """Возвращает список типов об-ов инт. собств."""
    return list(ObjKind.objects.order_by('pk').values('pk', 'title', 'sis_id'))


def get_claim_kinds(bool_as_int: bool = False) -> List[dict]:
    """Возвращает список видов обращений."""
    claim_kinds = list(ClaimKind.objects.order_by('pk').values('pk', 'title', 'obj_kind_id', 'third_person'))
    if bool_as_int:
        for claim_kind in claim_kinds:
            claim_kind['third_person'] = int(claim_kind['third_person'])
    return claim_kinds


def get_doc_types_for_consideration(claim_kind_id: Type[int]) -> List[dict]:
    """Возвращает список документов, которые должны быть сгенерированы на этапе приёма дела к рассмотрению."""
    doc_types = DocumentType.objects.filter(
        claim_kinds__id=claim_kind_id,
        code__in=['0006', '0007', '0009', '0010', '0011']
    ).values('pk', 'title', 'template', 'code')
    return list(doc_types)
