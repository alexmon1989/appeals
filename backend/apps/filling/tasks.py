from core.celery import app
from . import services as filling_services
from ..users import services as users_services
from ..classifiers import services as classifiers_services


@app.task
def get_app_data_from_es_task(obj_num_type: str,
                              obj_number: str,
                              obj_kind_id_sis: int,
                              obj_state: int,
                              cert_names: list) -> dict:
    """Возвращает данные объекта напрямую из ElasticSearch СИС."""
    hit = filling_services.application_get_data_from_es(obj_num_type, obj_number, obj_kind_id_sis, obj_state)

    res = {}

    # Проверка есть ли данные этого объекта и имеет ли пользователь доступ к данным
    if hit and (filling_services.application_is_published(hit)
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
    """Создаёт обращение."""
    user = users_services.user_get_or_create_from_cert(cert_data)
    claim = filling_services.claim_create(post_data, files_data, user)
    return {'claim_url': claim.get_absolute_url()}
