from core.celery import app
from .services import application_user_belongs_to_app, application_is_published, application_get_data_from_es


@app.task
def get_app_data_from_es(obj_num_type: str,
                         obj_number: str,
                         obj_kind_id_sis: int,
                         obj_state: int,
                         cert_names: list) -> dict:
    """Возвращает данные объекта напрямую из ElasticSearch СИС."""
    hit = application_get_data_from_es(obj_num_type, obj_number, obj_kind_id_sis, obj_state)

    res = {}

    # Проверка есть ли данные этого объекта и имеет ли пользователь доступ к данным
    if hit and (application_is_published(hit) or application_user_belongs_to_app(hit, cert_names)):
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
