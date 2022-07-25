from django.test import TestCase, override_settings
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from .. import services

from ...cases.models import DocumentTemplate
from ...classifiers.models import DocumentType
from ..models import Claim

import base64
import shutil
import os


UserModel = get_user_model()


class ClaimClass(TestCase):
    fixtures = [
        settings.FIXTURES_PATH / "classifiers.json",
        settings.FIXTURES_PATH / "claim_fields.json",
    ]

    @classmethod
    def setUpTestData(cls):
        cls.user = UserModel.objects.create(email="test@test.com", password='123456789')
        # Тестовый файл в формате base64
        with open(settings.FIXTURES_PATH / 'files' / 'test_files' / 'Текстовий_файл_1.docx', 'rb') as f:
            cls.file_test_base_64_content_1 = base64.b64encode(f.read()).decode("utf-8")

    def create_document_templates(self):
        """Создает шаблоны документов."""
        # Заперечення проти рішення НОІВ за заявкою (апелянт - заявник)
        file_name = 'Заперечення_проти_рішення_НОІВ_за_заявкою_апелянт_-_заявник.docx'
        with open(settings.FIXTURES_PATH / 'files' / 'templates' / file_name, 'rb') as f:
            base64_str = base64.b64encode(f.read()).decode("utf-8")
        doc_template = DocumentTemplate.objects.create(
            title='Заперечення проти рішення НОІВ за заявкою (апелянт - заявник)'
        )
        file_content = ContentFile(base64.b64decode(base64_str))
        doc_template.file.save(file_name, file_content)
        doc_template.documents_types.add(DocumentType.objects.get(code='0001'))


    def setUp(self):
        # Setup run before every test method.
        pass

    def tearDown(self):
        # Clean up run after every test method.
        media_test_path = settings.BASE_DIR / "../media_test"
        if os.path.exists(media_test_path):
            shutil.rmtree(media_test_path)

    def test_claim_process_input_data(self):
        """Тестирует функцию claim_process_input_data."""
        self.assertDictEqual(
            services.claim_process_input_data({
                'key_1': 'value 1',
                'key_2': 'value 2',
                'key_3': 'value 3',
                'key_4_date': '19.07.2022',
                'key_5': '19.07.2022',
            }),
            {
                'key_1': 'value 1',
                'key_2': 'value 2',
                'key_3': 'value 3',
                'key_4_date': '2022-07-19',
                'key_5': '19.07.2022',
            }
        )

    @override_settings(MEDIA_ROOT=(settings.BASE_DIR / "../media_test"))
    def test_claim_create(self):
        """Тестирует функцию claim_create."""
        self.create_document_templates()

        # Входящие данные
        input_data = {
            'post_data': {
                'obj_kind': 1,
                'claim_kind': 1,
                'app_number': 'a200000000',
                'third_person': 0,
                'obj_title': 'obj_title value',
                'app_date': '2022-07-20',
                'some_additional_data_1': 'value 1',
                'some_additional_data_2': 'value 2',
            },
            # Файлы в формате base64
            'files_data': {
                'appellant_reqs_claims': [{
                    'name': 'Текстовий файл.docx',
                    'content': self.file_test_base_64_content_1,
                }],
                'ukrpatent_decision': [{
                    'name': 'Текстовий файл.docx',
                    'content': self.file_test_base_64_content_1,
                }],
                'proof[]': [{
                    'name': 'Текстовий файл.docx',
                    'content': self.file_test_base_64_content_1,
                }],
                'representer_doc': [{
                    'name': 'Текстовий файл.docx',
                    'content': self.file_test_base_64_content_1,
                }],
                'payments_doc': [{
                    'name': 'Текстовий файл.docx',
                    'content': self.file_test_base_64_content_1,
                }],
            }
        }

        claim = services.claim_create(input_data['post_data'], input_data['files_data'], self.user)

        # self.assert
        claim_db = Claim.objects.get(pk=claim.pk)

        # Проверка корректности записанных данных обращения
        self.assertEqual(claim_db.status, 1)
        self.assertEqual(claim_db.obj_number, input_data['post_data']['app_number'])
        self.assertEqual(claim_db.third_person, input_data['post_data']['third_person'])
        self.assertEqual(claim_db.obj_kind_id, input_data['post_data']['obj_kind'])
        self.assertEqual(claim_db.claim_kind_id, input_data['post_data']['claim_kind'])
        self.assertEqual(claim_db.document_set.count(), len(input_data['files_data']) + 1)
