from django.test import TestCase, override_settings
from ..services import services
from ..models import Document


class ServicesTest(TestCase):
    def setUp(self):
        # Setup run before every test method.
        pass

    def tearDown(self):
        # Clean up run after every test method.
        pass

    @override_settings(DEBUG=True)
    def test_document_set_reg_number(self):
        new_doc = Document.objects.create(
            file='test_file'
        )
        self.assertIsNone(new_doc.registration_number)
        services.document_set_reg_number(new_doc.id)
        changed_doc = Document.objects.get(pk=new_doc.id)
        self.assertIsNotNone(changed_doc.registration_number)
        self.assertRegex(changed_doc.registration_number, r"Вх-\d{5}/2022")

    @override_settings(DEBUG=True)
    def test_document_set_barcode(self):
        new_doc = Document.objects.create(
            file='test_file'
        )
        self.assertIsNone(new_doc.barcode)
        services.document_set_barcode(new_doc.id)
        changed_doc = Document.objects.get(pk=new_doc.id)
        self.assertIsNotNone(changed_doc.barcode)
        self.assertRegex(changed_doc.barcode, r"\d{32}")
