from django.conf import settings

from core.celery import app
from . import services as filling_services
from apps.cases.services import case_services
from apps.users import services as users_services
from apps.classifiers import services as classifiers_services

import os
import time


@app.task
def get_app_data_from_es_task(obj_num_type: str,
                              obj_number: str,
                              obj_kind_id_sis: int,
                              obj_state: int,
                              cert_names: list = None,
                              internal_user: bool = False) -> dict:
    """Возвращает данные объекта напрямую из ElasticSearch СИС."""
    hit = filling_services.application_get_data_from_es(obj_num_type, obj_number, obj_kind_id_sis, obj_state)

    res = {}

    # Проверка есть ли данные этого объекта и имеет ли пользователь доступ к данным
    if hit and (internal_user
                or filling_services.application_is_published(hit)
                or filling_services.application_user_belongs_to_app(hit, cert_names)):
        # Возврат только библиографических данных
        if obj_kind_id_sis in (1, 2, 3):
            if obj_state == 1:
                res['data'] = hit['Claim']
            else:
                res['data'] = hit['Patent']
        elif obj_kind_id_sis == 4:
            res['data'] = hit['TradeMark']['TrademarkDetails']
        elif obj_kind_id_sis == 5:
            res['data'] = hit['Geo']['GeoDetails']
        elif obj_kind_id_sis == 6:
            res['data'] = hit['Design']['DesignDetails']

    return res


@app.task
def get_filling_form_data_task() -> dict:
    """Возвращает данные для формы подачи обращения."""
    return {
        # Типы объектов
        'obj_kinds': classifiers_services.get_obj_kinds_list(),
        # Типы обращений
        'claim_kinds': classifiers_services.get_claim_kinds(bool_as_int=True),
        # Возможные поля обращений (зависящие от типа)
        'claim_fields': filling_services.claim_get_fields(bool_as_int=True)
    }


@app.task
def create_claim_task(post_data, files_data, cert_data: dict) -> dict:
    """Создаёт обращение (вызывается из внешнего модуля)."""
    user = users_services.user_get_or_create_from_cert(cert_data)
    claim = filling_services.claim_create(post_data, files_data, user)
    return {'claim_url': claim.get_absolute_url()}


@app.task
def create_claim_task_internal(post_data, files_data, user_id: int) -> dict:
    """Создаёт обращение (вызывается из внутреннего модуля)."""
    user = users_services.user_get_by_pk(user_id)
    claim = filling_services.claim_create(post_data, files_data, user, True)
    return {'claim_url': claim.get_absolute_url()}


@app.task
def edit_claim_task(claim_id, post_data, files_data, cert_data: dict) -> dict:
    """Редактирует обращение."""
    user = users_services.user_get_or_create_from_cert(cert_data)
    claim = filling_services.claim_edit(claim_id, post_data, files_data, user)
    return {'claim_url': claim.get_absolute_url()}


@app.task
def edit_claim_task_internal(claim_id, post_data, files_data, user_id: int) -> dict:
    """Редактирует обращение (вызывается из внутреннего модуля)."""
    user = users_services.user_get_by_pk(user_id)
    claim = filling_services.claim_edit(claim_id, post_data, files_data, user)
    return {'claim_url': claim.get_absolute_url()}


@app.task
def get_claim_data_task(claim_id: int, cert_data: dict, **kwargs) -> dict:
    """Возвращает данные обращения пользователя."""
    # Получение данных обращения
    user = users_services.user_get_or_create_from_cert(cert_data)
    claim = filling_services.claim_get_data_by_id(claim_id, user, **kwargs)

    # Копирование документов обращения
    if claim:
        filling_services.claim_copy_docs_to_external_server(claim_id)

    return claim


@app.task
def get_claim_data_task_internal(claim_id: int, user_id: int, **kwargs) -> dict:
    """Возвращает данные обращения пользователя (вызывается из внешнего модуля)."""
    # Получение данных обращения
    user = users_services.user_get_by_pk(user_id)
    claim = filling_services.claim_get_data_by_id(claim_id, user, **kwargs)
    return claim


@app.task
def get_claim_status(claim_id: int, cert_data: dict) -> dict:
    """Возвращает данные статуса обращения пользователя."""
    user = users_services.user_get_or_create_from_cert(cert_data)
    claim = filling_services.claim_get_user_claims_qs(user).filter(pk=claim_id).first()

    if claim:
        return {
            'success': 1,
            'data': {
                'status_code': claim.status,
                'status_verbal': claim.get_status_display()
            }
        }

    return {'success': 0, 'message': 'not found'}


@app.task
def delete_claim_task(claim_id: int, cert_data: dict) -> dict:
    """Удаляет обращение пользователя."""
    user = users_services.user_get_or_create_from_cert(cert_data)
    claim = filling_services.claim_get_user_claims_qs(user).filter(pk=claim_id, status__lt=3).first()
    if claim:
        claim.delete()
        return {'success': 1}
    return {'success': 0, 'message': 'not found'}


@app.task
def delete_claim_task_internal(claim_id: int, user_id: int) -> dict:
    """Удаляет обращение пользователя (вызывается из внутреннего модуля)."""
    user = users_services.user_get_by_pk(user_id)
    claim = filling_services.claim_get_user_claims_qs(user).filter(pk=claim_id, status__lt=3).first()
    if claim:
        claim.delete()
        return {'success': 1}
    return {'success': 0, 'message': 'not found'}


@app.task
def create_case_task(claim_id: int, cert_data: dict) -> dict:
    user = users_services.user_get_or_create_from_cert(cert_data)
    case = case_services.case_create_from_claim(claim_id, user)
    if case:
        return {'success': 1, 'case_number': case.case_number}
    return {'success': 0, 'message': 'Ви не можете передати звернення, тому що документи не було підписано.'}


@app.task
def create_case_task_internal(claim_id: int, user_id: int) -> dict:
    user = users_services.user_get_by_pk(user_id)
    case = case_services.case_create_from_claim(claim_id, user)
    if case:
        return {'success': 1, 'case_number': case.case_number}
    return {'success': 0, 'message': 'Ви не можете передати звернення, тому що документи не було підписано.'}


@app.task
def get_claim_list_task(cert_data: dict) -> list:
    """Возвращает список обращений пользователя."""
    res = []
    user = users_services.user_get_or_create_from_cert(cert_data)
    claims = filling_services.claim_get_user_claims_qs(user).order_by('-created_at')
    for claim in claims:
        item = {
            'obj_number': claim.obj_number,
            'absolute_url': claim.get_absolute_url(),
            'obj_kind': claim.obj_kind.title,
            'claim_kind': claim.claim_kind.title,
            'status': claim.status,
            'status_display': claim.get_status_display(),
            'case_number': '',
            'created_at': claim.created_at.strftime('%d.%m.%Y %H:%M:%S'),
            'created_at_timestamp': claim.created_at.timestamp(),
        }
        if claim.status == 3:
            item['case_number'] = claim.case.case_number
        res.append(item)
    return res


@app.task
def get_claim_list_task_internal(user_id: int) -> list:
    """Возвращает список обращений пользователя (вызывается из внутреннего модуля)."""
    res = []
    user = users_services.user_get_by_pk(user_id)
    claims = filling_services.claim_get_user_claims_qs(user).order_by('-created_at')
    for claim in claims:
        item = {
            'obj_number': claim.obj_number,
            'absolute_url': claim.get_absolute_url(),
            'obj_kind': claim.obj_kind.title,
            'claim_kind': claim.claim_kind.title,
            'status': claim.status,
            'status_display': claim.get_status_display(),
            'case_number': '',
            'created_at': claim.created_at.strftime('%d.%m.%Y %H:%M:%S'),
            'created_at_timestamp': claim.created_at.timestamp(),
        }
        if claim.status == 3:
            item['case_number'] = claim.case.case_number
        res.append(item)
    return res


@app.task
def create_files_with_signs_info_task(cert_data: dict, claim_id: int, signs: list) -> bool:
    """Создаёт файлы документов с информацией о цифровой подписи."""
    user = users_services.user_get_or_create_from_cert(cert_data)
    claim = filling_services.claim_get_user_claims_qs(user).filter(pk=claim_id, status__in=[1, 2]).first()

    if claim:
        filling_services.claim_create_files_with_signs_info(claim_id, signs)
        filling_services.claim_copy_docs_to_external_server(claim_id)
        return True

    return False


@app.task
def clear_external_documents_folder(older_than_min: int = 60) -> None:
    """Очищает каталог path. Удаляет файлы старше older_than_min минут, а затем удаляет пустые каталоги."""
    for address, dirs, files in os.walk(settings.EXTERNAL_MEDIA_ROOT):
        # Удаление старых файлов
        for file in files:
            full_path = os.path.join(address, file)
            if os.stat(full_path).st_mtime < (time.time() - older_than_min*60):
                os.remove(full_path)

        # Удаление пустых каталогов
        for dir_ in dirs:
            full_path = os.path.join(address, dir_)
            if not os.listdir(full_path):
                os.rmdir(full_path)
