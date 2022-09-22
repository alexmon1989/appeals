from django import template
from django.contrib.auth import get_user_model

from apps.cases.services import document_can_be_signed_by_user
from apps.cases.models import Document

register = template.Library()
UserModel = get_user_model()


@register.simple_tag
def user_can_sign_document(document: Document, user: UserModel):
    """Может ли пользователь подписывать документ."""
    return document_can_be_signed_by_user(document.pk, user)
