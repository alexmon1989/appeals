from django.db import connection


def stat_get_data(code: str, date_from: str, date_to: str) -> list:
    """Вызывает хранимую процедуру stat_annex_{code} и возвращает данные.
    Параметры date_from, date_to д.б. в формате гггг-мм-дд."""
    with connection.cursor() as cursor:
        cursor.execute(f"SET NOCOUNT ON; EXEC stat_annex_{code} @startdate = %s, @enddate = %s", (date_from, date_to))
        data = cursor.fetchall()
        return data
