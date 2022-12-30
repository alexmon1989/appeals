from django import forms
from django.core.exceptions import ValidationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column


TYPES = (
    ('', 'Оберіть показник...'),
    ('6_1_1', 'Кількість звернень (заперечення, апеляційні заяви, заяви про визнання ТМ ДВ), '
              'що надійшли на розгляд АП, в заданий проміжок часу (за об\'єктами)'),
    ('6_1_2', 'Кількість звернень (заперечення, апеляційні заяви, заяви про визнання ТМ ДВ), '
              'що надійшли на розгляд АП, в заданий проміжок часу (за видами звернень)'),
    ('6_2_1', 'Кількість звернень за видами осіб, що подані в заданий проміжок часу'),
    ('6_3_1', 'Кількість звернень за видами звернень, за ОПІВ за період часу'),
    ('6_4_1', 'Кількість поданих звернень за підставами для відмови у наданні правової охорони (заперечення), '
              'за підставами визнання патентів, свідоцтв недійсними'),
    ('6_5_1', 'Кількість проведених засідань за період часу'),
    ('6_6_1', 'Кількість оголошених рішень у розрізі об’єктів, видів звернень за період часу'),
    ('6_7_1', 'Кількість затверджених рішень (виданих наказів) за період часу у розрізі об’єктів, видів звернень, '
              'видів рішень'),
    ('6_8_1', 'Середній строк розгляду заперечення'),
    ('6_9_1', 'Кількість розглянутих звернень членами Апеляційної палати у розрізі об’єктів, '
              'видів звернень за період часу'),
    ('6_9_1', 'Кількість звернень, що знаходяться розгляді на певну дату за кожним членом АП і всього за період часу '
              'у розрізі об’єктів, звернень'),
)


class StatForm(forms.Form):
    """Форма статистичного звіту."""
    stat_type = forms.ChoiceField(
        choices=TYPES,
        label='Показник',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select-sm'})
    )
    date_from = forms.DateField(
        label='Дата (від)',
        required=True,
        widget=forms.DateInput(
            attrs={'placeholder': 'Дата (від)', 'class': 'form-control-sm', 'type': 'date'}
        )
    )
    date_to = forms.DateField(
        label='Дата(до)',
        required=True,
        widget=forms.DateInput(
            attrs={'placeholder': 'Дата (до)', 'class': 'form-control-sm', 'type': 'date'}
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.label_class = "fw-bold"
        self.helper.form_tag = False
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            'stat_type',
            Row(
                Column('date_from', css_class='form-group col-md-6 mb-0'),
                Column('date_to', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
        )
