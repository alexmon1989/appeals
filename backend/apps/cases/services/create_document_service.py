from django.contrib.auth import get_user_model

from apps.cases.models import Document, Case
from apps.classifiers.models import DocumentType

from .document_services import document_set_barcode, document_set_reg_number, document_add_history
from apps.common.utils import (docx_replace, first_lower, get_random_file_name, get_temp_file_path,
                               generate_barcode_img, substitute_image_docx)

from docx import Document as PyDocxDocument

from pathlib import Path
import datetime

UserModel = get_user_model()


class Service:
    case: Case
    document: Document
    doc_type: DocumentType
    user_id: int
    signer: UserModel
    file_vars = {}
    extra_args = {}

    def _get_file_vars(self) -> dict:
        """Формирует список с переменными для замены в файле docx."""
        if self.doc_type.code == '0005':
            return get_file_vars_0005(self.case, self.document, self.signer)
        elif self.doc_type.code == '0006':
            return get_file_vars_0006(self.case, self.document)
        elif self.doc_type.code == '0007':
            return get_file_vars_0007(self.case, self.document)
        else:
            return {}

    def _create_doc_file(self) -> Path:
        """Создаёт файл на диске."""
        # Открытие файла с шаблоном
        docx = PyDocxDocument(self.doc_type.template.path)

        # Получение и замена переменных в файле
        docx_replace(docx, self.file_vars)

        # Создание и помещение штрих-кода в файл
        barcode_file_path = generate_barcode_img(self.document.barcode)

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

    def _create_doc_db(self) -> Document:
        """Создаёт документ в БД (без ссылки на файл)."""
        doc = Document.objects.create(
            case=self.case,
            document_type=self.doc_type,
            input_date=datetime.datetime.now(),
            auto_generated=True,
        )
        document_add_history(
            doc.pk,
            'Документ додано у систему (створено автоматично)',
            self.user_id
        )
        document_set_barcode(doc.pk)
        document_set_reg_number(doc.pk)
        doc.refresh_from_db()
        return doc

    def execute(self, case_id: int, signer_id: int, doc_code: str, user_id: int, **kwargs) -> Document:
        self.user_id = user_id
        self.signer = UserModel.objects.get(pk=signer_id)
        self.extra_args = kwargs
        self.case = Case.objects.select_related('claim').get(pk=case_id)
        self.doc_type = DocumentType.objects.get(
            code=doc_code,
            claim_kinds__id=self.case.claim.claim_kind_id
        )
        self.document = self._create_doc_db()
        self.file_vars = self._get_file_vars()
        doc_file_path = self._create_doc_file()
        self.document.assign_file(doc_file_path)
        return self.document


def get_file_vars_0005(case: Case, document: Document, signer: UserModel) -> dict:
    """Возвращает словарь со значениями переменных для формирования документа с кодом 0005."""
    # Члены коллегии
    common_members = []
    head_title = ''
    head_position = ''
    for member in case.collegiummembership_set.all():
        if member.is_head:
            head_title = member.person.get_full_name
            head_position = first_lower(member.person.position)
        else:
            common_members.append(
                {
                    'title': member.person.get_full_name,
                    'position': first_lower(member.person.position)
                }
            )

    # Апелянт
    appellant = case.claim.get_appellant_title()

    case_extra_info = f"апелянт - {appellant}"
    if case.claim.claim_kind.claim_sense == 'DE':
        case_extra_info += f", номер заявки: {case.claim.obj_number}"

    if case.claim.third_person:
        if case.claim.claim_kind.claim_sense == 'DE':
            case_extra_info += f", заявник: {case.claim.get_applicant_title()}"
        else:
            case_extra_info += f"номер охоронного документа: {case.claim.obj_number}, " \
                               f"власник: {case.claim.get_owner_title()}"

    return {
        '{{ DATE }}': document.input_date.strftime("%d.%m.%Y"),
        '{{ DOC_NUMBER }}': document.registration_number,
        '{{ CASE_NUMBER }}': case.case_number,
        '{{ CLAIM_KIND }}': first_lower(case.claim.claim_kind.template_title),
        '{{ OBJ_KIND }}': first_lower(case.claim.obj_kind.title),
        '{{ OBJ_TITLE }}': case.claim.obj_title,
        '{{ CASE_EXTRA_INFO }}': case_extra_info,
        '{{ HEAD_TITLE }}': head_title,
        '{{ HEAD_POSITION }} ': head_position,
        '{{ MEMBER_1_TITLE }}': common_members[0]['title'],
        '{{ MEMBER_1_POSITION }}': common_members[0]['position'],
        '{{ MEMBER_2_TITLE }}': common_members[1]['title'],
        '{{ MEMBER_2_POSITION }}': common_members[1]['position'],
        '{{ SECRETARY_TITLE }}': case.secretary.get_full_name,
        '{{ SECRETARY_POSITION }}': case.secretary.position,
        '{{ SIGNER_TITLE }}': signer.get_full_name,
        '{{ SIGNER_POSITION }}': signer.position,
    }


def get_file_vars_0006(case: Case, document: Document) -> dict:
    """Возвращает словарь со значениями переменных для формирования документа с кодом 0006
    (сообщение апеллянту о принятии дела к рассмотрению)."""
    # Представитель апеллянта или апеллянт
    represent = case.claim.get_represent_title(third_person=case.claim.third_person)
    if represent:
        header_person_title = represent
        header_person_address = case.claim.get_represent_address()
    else:
        header_person_title = case.claim.get_appellant_title()
        header_person_address = case.claim.get_appellant_address()

    # Документ обращения
    claim_doc = Document.objects.get(document_type__code__in=('0001', '0002'), claim=case.claim)
    claim_doc_reg_num = claim_doc.registration_number
    claim_doc_reg_date = claim_doc.input_date.strftime("%d.%m.%Y")

    # Коллегия
    collegium_head = ''
    collegium = []
    for item in case.collegiummembership_set.all():
        collegium.append(item.person.get_full_name_initials())
        if item.is_head:
            collegium_head = item.person.get_full_name
    return {
        '{{ DOC_REG_DATE }}': document.input_date.strftime("%d.%m.%Y"),
        '{{ DOC_REG_NUM }}': document.registration_number,
        '{{ HEADER_PERSON_TITLE }}': header_person_title,
        '{{ HEADER_PERSON_ADDRESS }}': header_person_address,
        '{{ CLAIM_DOC_REG_NUM }}': claim_doc_reg_num,
        '{{ CLAIM_DOC_REG_DATE }}': claim_doc_reg_date,
        '{{ OBJ_KIND_TITLE }}': first_lower(case.claim.obj_kind.title),
        '{{ OBJ_TITLE }}': case.claim.obj_title,
        '{{ APP_NUMBER }}': case.claim.obj_number,
        '{{ APPELAINT_TITLE }}': case.claim.get_appellant_title(),
        '{{ APPELAINT_ADDRESS }}': case.claim.get_appellant_address(),
        '{{ APPLICANT_TITLE }}': case.claim.get_applicant_title(),
        '{{ APPLICANT_ADDRESS }}': case.claim.get_applicant_address(),
        '{{ COLLEGIUM_MEMBERS }}': ', '.join(collegium),
        '{{ SECRETARY_EMAIL }}': case.secretary.email,
        '{{ COLLEGIUM_HEAD }}': collegium_head,
        '{{ SECRETARY_TITLE }}': case.secretary.get_full_name,
        '{{ SECRETARY_PHONE }}': case.secretary.phone_number or '',
    }


def get_file_vars_0007(case: Case, document: Document) -> dict:
    """Возвращает словарь со значениями переменных для формирования документа с кодом 0007
    (сообщение заявителю о принятии дела к рассмотрению)."""
    # Представитель заявителя или заявитель
    represent = case.claim.get_represent_title()
    if represent:
        header_person_title = represent
        header_person_address = case.claim.get_represent_address()
    else:
        header_person_title = case.claim.get_applicant_title()
        header_person_address = case.claim.get_applicant_address()

    # Документ обращения
    claim_doc = Document.objects.get(document_type__code__in=('0001', '0002'), claim=case.claim)
    claim_doc_reg_num = claim_doc.registration_number
    claim_doc_reg_date = claim_doc.input_date.strftime("%d.%m.%Y")

    # Коллегия
    collegium_head = ''
    collegium = []
    for item in case.collegiummembership_set.all():
        collegium.append(item.person.get_full_name_initials())
        if item.is_head:
            collegium_head = item.person.get_full_name

    return {
        '{{ DOC_REG_DATE }}': document.input_date.strftime("%d.%m.%Y"),
        '{{ DOC_REG_NUM }}': document.registration_number,
        '{{ HEADER_PERSON_TITLE }}': header_person_title,
        '{{ HEADER_PERSON_ADDRESS }}': header_person_address,
        '{{ CLAIM_DOC_REG_NUM }}': claim_doc_reg_num,
        '{{ CLAIM_DOC_REG_DATE }}': claim_doc_reg_date,
        '{{ OBJ_KIND_TITLE }}': first_lower(case.claim.obj_kind.title),
        '{{ OBJ_TITLE }}': case.claim.obj_title,
        '{{ APP_NUMBER }}': case.claim.obj_number,
        '{{ APPELAINT_TITLE }}': case.claim.get_appellant_title(),
        '{{ APPELAINT_ADDRESS }}': case.claim.get_appellant_address(),
        '{{ APPLICANT_TITLE }}': case.claim.get_applicant_title(),
        '{{ APPLICANT_ADDRESS }}': case.claim.get_applicant_address(),
        '{{ COLLEGIUM_MEMBERS }}': ', '.join(collegium),
        '{{ SECRETARY_EMAIL }}': case.secretary.email,
        '{{ COLLEGIUM_HEAD }}': collegium_head,
        '{{ SECRETARY_TITLE }}': case.secretary.get_full_name,
        '{{ SECRETARY_PHONE }}': case.secretary.phone_number or '',

        '{{ DOC_DOWNLOAD_CODE }}': claim_doc.barcode[-10:],  # последние 10 цифр штрих-кода
    }
