from django import template
from django.contrib.auth import get_user_model

from ..services import document_can_be_signed_by_user
from ..models import Document

register = template.Library()
UserModel = get_user_model()


@register.simple_tag
def user_can_sign_document(document: Document, user: UserModel):
    print(document, user)
    return document_can_be_signed_by_user(document, user)
