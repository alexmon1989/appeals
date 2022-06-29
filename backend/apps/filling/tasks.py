from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q

from django.conf import settings

from core.celery import app
from .services import application_user_belongs_to_app, application_is_published


@app.task
def test_task():
    return 'Success'


@app.task
def get_app_data_from_es(obj_num_type: str,
                         obj_number: str,
                         obj_kind_id_sis: int,
                         obj_state: int,
                         cert_names: list) -> dict:
    """Возвращает данные объекта напрямую из ElasticSearch СИС."""
    client = Elasticsearch(settings.ELASTIC_HOST, timeout=settings.ELASTIC_TIMEOUT)

    if obj_num_type == 'registration_number':
        obj_num_type = 'protective_doc_number'

    query_string = f"search_data.{obj_num_type}.exact:{obj_number} AND " \
                   f"Document.idObjType:{obj_kind_id_sis} AND " \
                   f"search_data.obj_state:{obj_state}"

    q = Q(
        'query_string',
        query=query_string
    )

    s = Search(using=client, index=settings.ELASTIC_INDEX_NAME).query(q).execute()

    if not s:
        return {}
    hit = s[0].to_dict()

    res = {}

    # Проверка имеет ли пользователь доступ к данным заявки
    if not application_is_published(hit) and not application_user_belongs_to_app(hit, cert_names):
        return res

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
