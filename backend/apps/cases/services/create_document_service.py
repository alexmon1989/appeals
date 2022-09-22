from django.contrib.auth import get_user_model

from apps.cases.models import Document
from apps.classifiers.models import DocumentType

from .document_services import document_set_barcode, document_set_reg_number
from apps.common.utils import (docx_replace, first_lower, get_random_file_name, get_temp_file_path, generate_barcode_img,
                             substitute_image_docx)

from docx import Document as PyDocxDocument

from abc import ABC, abstractmethod
from pathlib import Path
import datetime


UserModel = get_user_model()


class DocumentCreatorService(ABC):
    """Абстрактный класс сервиса создания документа."""

    doc_type_code: str
    doc_type: DocumentType

    def _get_doc_type(self):
        """Получает из БД тип документа по коду."""
        self.doc_type = DocumentType.objects.filter(code=self.doc_type_code).first()

    def __init__(self):
        self._get_doc_type()

    @abstractmethod
    def execute(self, *args, **kwargs) -> Document:
        pass

    @abstractmethod
    def _create_doc_db(self, *args, **kwargs) -> Document:
        pass

    @abstractmethod
    def _create_doc_file(self, *args, **kwargs) -> Document:
        pass


class CaseDocumentCreatorService(DocumentCreatorService, ABC):
    """Базовый класс сервиса создания документа ап. дела."""

    def _create_doc_db(self, case_id: int) -> Document:
        """Создаёт документ в БД (без ссылки на файл)."""
        doc = Document.objects.create(
            case_id=case_id,
            document_type=self.doc_type,
            input_date=datetime.datetime.now(),
            auto_generated=True,
        )
        document_set_barcode(doc.pk)
        document_set_reg_number(doc.pk)
        doc.refresh_from_db()
        return doc

    @abstractmethod
    def _get_file_vars(self, doc: Document, signer_id: int) -> dict:
        """Формирует словарь с переменными для последующей замены их в файле Word."""
        pass

    def _create_doc_file(self, doc: Document, signer_id: int) -> Path:
        """Создаёт файл на диске."""
        # Открытие файла с шаблоном
        docx = PyDocxDocument(self.doc_type.template.path)

        # Получение и замена переменных в файле
        docx_replace(docx, self._get_file_vars(doc, signer_id))

        # Создание и помещение штрих-кода в файл
        barcode_file_path = generate_barcode_img(doc.barcode)

        substitute_image_docx(docx, '{{ BARCODE_IMG }}', barcode_file_path, 6)

        def iter_target_paragraphs(document):
            """Generate each paragraph inside all tables of `document`."""
            for table in document.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for paragraph in cell.paragraphs:
                            yield paragraph

        def substitute_image_placeholder(paragraph, image_var, barcode_file):
            # --- start with removing the placeholder text ---
            paragraph.text = paragraph.text.replace(image_var, "")
            # --- then append a run containing the image ---
            run = paragraph.add_run()
            from docx.shared import Cm
            run.add_picture(barcode_file, height=Cm(6))

        for paragraph in iter_target_paragraphs(docx):
            if '{{ BARCODE_IMG }}' in paragraph.text:
                substitute_image_placeholder(paragraph, '{{ BARCODE_IMG }}', str(barcode_file_path))

        # Сохранение файла во временный каталог
        tmp_file_name = get_random_file_name('docx')
        tmp_file_path = get_temp_file_path(tmp_file_name)
        docx.save(tmp_file_path)
        return tmp_file_path

    def execute(self, case_id: int, signer_id: int, *args, **kwargs) -> Document:
        doc = self._create_doc_db(case_id)
        doc_file_path = self._create_doc_file(doc, signer_id)
        doc.assign_file(doc_file_path)
        return doc


class CollegiumDocumentCreatorService(CaseDocumentCreatorService):
    """Создаёт документ распоряжения о создании коллегии."""
    doc_type_code = '0005'

    def _get_file_vars(self, doc: Document, signer_id: int) -> dict:
        # Члены коллегии
        common_members = []
        head_title = ''
        head_position = ''
        for member in doc.case.collegiummembership_set.all():
            if member.is_head:
                head_title = member.person.get_full_name
                head_position = first_lower(member.person.position)
            else:
                common_members.append(
                    {
                        'title':  member.person.get_full_name,
                        'position': first_lower(member.person.position)
                    }
                )

        # Подписант
        signer = UserModel.objects.filter(pk=signer_id).first()

        claim = doc.case.claim

        # Апелянт
        appellant = claim.get_appellant_title()

        case_extra_info = f"апелянт - {appellant}"
        if claim.claim_kind.claim_sense == 'DE':
            case_extra_info += f", номер заявки: {claim.obj_number}"

        if claim.third_person:
            if claim.claim_kind.claim_sense == 'DE':
                case_extra_info += f", заявник: {claim.get_applicant_title()}"
            else:
                case_extra_info += f"номер охоронного документа: {claim.obj_number}, власник: {claim.get_owner_title()}"

        return {
            '{{ DATE }}': doc.input_date.strftime("%d.%m.%Y"),
            '{{ DOC_NUMBER }}': doc.registration_number,
            '{{ CASE_NUMBER }}': doc.case.case_number,
            '{{ CLAIM_KIND }}': first_lower(claim.claim_kind.template_title),
            '{{ OBJ_KIND }}': first_lower(claim.obj_kind.title),
            '{{ OBJ_TITLE }}': claim.obj_title,
            '{{ CASE_EXTRA_INFO }}': case_extra_info,
            '{{ HEAD_TITLE }}': head_title,
            '{{ HEAD_POSITION }} ': head_position,
            '{{ MEMBER_1_TITLE }}': common_members[0]['title'],
            '{{ MEMBER_1_POSITION }}': common_members[0]['position'],
            '{{ MEMBER_2_TITLE }}': common_members[1]['title'],
            '{{ MEMBER_2_POSITION }}': common_members[1]['position'],
            '{{ SECRETARY_TITLE }}': doc.case.secretary.get_full_name,
            '{{ SECRETARY_POSITION }}': doc.case.secretary.position,
            '{{ SIGNER_TITLE }}': signer.get_full_name,
            '{{ SIGNER_POSITION }}': signer.position,
        }
