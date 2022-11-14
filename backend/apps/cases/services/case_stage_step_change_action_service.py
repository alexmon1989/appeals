from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib import messages

from apps.cases.models import Case, CaseStageStep
from apps.classifiers import services as classifiers_services
from .case_services import case_change_stage_step, case_get_all_persons, case_create_docs

from apps.classifiers.services import get_doc_types_for_meeting
from apps.notifications.services import Service as NotificationService


UserModel = get_user_model()


class CaseStageStepQualifier:
    """Класс, задачей которого есть определить фактическую стадию ап. дела (например, по подписанным документам)."""
    case: Case

    def __init__(self):
        # Функции проверки стадий
        self.stages_checks = {
            2000: self._satisfies_2000,
            2001: self._satisfies_2001,
            2002: self._satisfies_2002,
            2003: self._satisfies_2003,
            2004: self._satisfies_2004,
            2005: self._satisfies_2005,
            2006: self._satisfies_2006,
            3000: self._satisfies_3000,
            3001: self._satisfies_3001,
            3002: self._satisfies_3002,
            4000: self._satisfies_4000,
        }

    def _satisfies_2000(self):
        """Удовлетворяет условиям стадии 2000 "Прийнято в роботу. Очікує на заповнення досьє."."""
        return self.case.stage_step.code == 1000

    def _satisfies_2001(self):
        """Удовлетворяет условиям стадии 2001 "Досьє заповнено. Очікує на розподіл колегії."."""
        return self.case.stage_step.code == 2000

    def _satisfies_2002(self):
        """Удовлетворяет условиям стадии 2002 "Здійснено розподіл колегії. Очікує на підписання розпорядження."."""
        return self.case.stage_step.code == 2001 and self.case.collegiummembership_set.count() > 0

    def _satisfies_2003(self):
        """Удовлетворяет условиям стадии 2003 "Розпорядження підписано. Очікує на прийняття до розгляду."."""
        if self.case.stage_step.code == 2002:
            # Коды документов, которые д.б. подписаны
            doc_codes_to_sign = ['0005', '0028']
            for document in self.case.document_set.all():
                if document.document_type.code in doc_codes_to_sign and document.is_signed_by_head:
                    doc_codes_to_sign.remove(document.document_type.code)
            return len(doc_codes_to_sign) == 0
        return False

    def _satisfies_2004(self):
        """Удовлетворяет условиям стадии 2003 "Документи для прийняття справи до розгляду очікують на підписання."."""
        if self.case.stage_step.code == 2003:
            # Множество кодов документов, которые должны присутствовать на стадии
            doc_types_should_exist = {
                x['code'] for x in classifiers_services.get_doc_types_for_consideration(self.case.claim.claim_kind_id)
            }

            # Множество кодов документов, которые присутствуют у дела
            doc_types_current = {
                x.document_type.code for x in self.case.document_set.select_related('document_type').all()
            }

            # Проверка есть ли коды документов, которые должны присутствовать на стадии, в текущих документах дела
            return doc_types_should_exist.issubset(doc_types_current)

        return False

    def _satisfies_2005(self):
        """Удовлетворяет условиям стадии 2005 "Справу прийнято до розгляду. Створене підготовче засідання."."""
        if self.case.stage_step.code == 2004:
            # Множество кодов документов, которые должны присутствовать на стадии
            doc_types_should_exist = {
                x['code'] for x in classifiers_services.get_doc_types_for_consideration(self.case.claim.claim_kind_id)
            }

            # Множество кодов документов, которые присутствуют у дела
            doc_types_current = {
                x.document_type.code for x in self.case.document_set.select_related('document_type').all()
            }

            # Проверка есть ли коды документов, которые должны присутствовать на стадии, в текущих документах дела
            if doc_types_should_exist.issubset(doc_types_current):
                # Проверка создано ли предварительное заседание
                return self.case.meeting_set.filter(meeting_type='PRE').exists()

        return False

    def _satisfies_2006(self):
        """Удовлетворяет условиям стадии 2006 "Створений протокол підготовчого засідання, чекає на підпис."."""
        if self.case.stage_step.code == 2005:
            # Множество кодов документов, которые должны присутствовать на стадии
            doc_types_should_exist = {
                x['code'] for x in classifiers_services.get_doc_types_for_pre_meeting_protocol(
                    self.case.claim.claim_kind_id
                )
            }

            # Множество кодов документов, которые присутствуют у дела
            doc_types_current = {
                x.document_type.code for x in self.case.document_set.select_related('document_type').all()
            }

            # Проверка есть ли коды документов, которые должны присутствовать на стадии, в текущих документах дела
            return doc_types_should_exist.issubset(doc_types_current)

        return False

    def _satisfies_3000(self):
        """Удовлетворяет условиям стадии 3000 "Справу прийнято до розгляду"."""
        if self.case.stage_step.code == 2004:
            # Множество кодов документов, которые должны присутствовать на стадии
            doc_types_should_exist = {
                x['code'] for x in classifiers_services.get_doc_types_for_consideration(self.case.claim.claim_kind_id)
            }

            # Множество кодов подписанных документов, которые присутствуют у дела
            doc_types_current = {
                x.document_type.code for x in self.case.document_set.all() if x.is_signed_by_head
            }

            # Проверка есть ли коды документов, которые должны присутствовать на стадии,
            # в текущих подписанных документах дела
            return doc_types_should_exist.issubset(doc_types_current)
        elif self.case.stage_step.code == 2006:
            # Проверка есть ли подписанный протокол предварительного заседания
            document = self.case.document_set.filter(document_type__code='0027').first()
            return document and document.is_signed

        return False

    def _satisfies_3001(self):
        """Удовлетворяет условиям стадии 3001 "Створене засідання АП. Чекає на погодження членів колегії."."""
        if self.case.stage_step.code == 3000:
            # Проверка что существует заседание с непринятыми приглашениями от всех членов коллегии
            meeting = self.case.meeting_set.prefetch_related('invitation_set').order_by('-pk').first()
            if meeting:
                for invitation in meeting.invitation_set.all():
                    if invitation.accepted_at:
                        return False
                return True
        return False

    def _satisfies_3002(self):
        """Удовлетворяет условиям стадии 3002 "Створене засідання АП. Чекає на підписання документів."."""
        if self.case.stage_step.code == 3001:
            # Проверка что существует заседание с принятыми приглашениями от всех членов коллегии
            meeting = self.case.meeting_set.prefetch_related('invitation_set').order_by('-pk').first()
            if meeting:
                for invitation in meeting.invitation_set.all():
                    if not invitation.accepted_at:
                        return False
                return True
        return False

    def _satisfies_4000(self):
        """Удовлетворяет условиям стадии 4000 "Чекає на проведення засідання Апеляційної палати."."""
        if self.case.stage_step.code == 3002:
            # Проверка что существует заседание с принятыми приглашениями от всех членов коллегии
            meeting = self.case.meeting_set.prefetch_related('invitation_set').order_by('-pk').first()
            if meeting:
                for invitation in meeting.invitation_set.all():
                    if not invitation.accepted_at:
                        return False

                # Множество кодов документов, которые должны присутствовать на стадии
                doc_types_should_exist = {
                    x['code'] for x in
                    classifiers_services.get_doc_types_for_meeting(self.case.claim.claim_kind_id)
                }

                # Множество кодов подписанных документов, которые присутствуют у дела
                doc_types_current = {
                    x.document_type.code for x in self.case.document_set.all() if x.is_signed_by_head
                }

                # Проверка есть ли коды документов, которые должны присутствовать на стадии,
                # в текущих подписанных документах дела
                return doc_types_should_exist.issubset(doc_types_current)

        return False

    def get_stage_step(self, case: Case) -> int:
        self.case = case
        # Проверка стадий в обратном порядке (от старшей к младшей)
        for stage in sorted(self.stages_checks.keys(), reverse=True):
            if self.stages_checks[stage]():
                return stage
        return 0


class CaseSetActualStageStepService:
    """Присваивает значение актуальной стадии ап. дела и производит сопутствующие стадии действия."""
    def __init__(self,
                 qualifier: CaseStageStepQualifier,
                 case: Case,
                 request,
                 notification_service: NotificationService):
        self.case = case
        self.qualifier = qualifier
        self.request = request
        self.notification_service = notification_service

    def _call_2000_actions(self):
        """Выполнение действий, характерных для стадии 2000 -
        "Прийнято в роботу. Очікує на заповнення досьє."."""
        self.case.secretary = self.request.user
        self.case.save()
        case_change_stage_step(self.case.pk, 2000, self.request.user.pk)
        self.case.refresh_from_db()
        self.notify_all_persons()

        # Отдельно для секретаря оповещение, что его назначено секретарём по делу
        # Текущий пользователь и есть секретарь, т.к. данную операцию проводит только пользователь с ролью секретарь
        case_url = reverse('cases-detail', kwargs={'pk': self.case.pk})
        message = f'Вас призначено секретарем по справі <b><a href="{case_url}">{self.case.case_number}</a></b>'
        messages.add_message(self.request, messages.SUCCESS, message)
        self.notification_service.execute(message, [self.request.user.pk])

    def _call_2001_actions(self):
        """Выполнение действий, характерных для стадии 2001 -
        "Досьє заповнено. Очікує на розподіл колегії."."""
        case_change_stage_step(self.case.pk, 2001, self.request.user.pk)
        self.case.refresh_from_db()
        self.notify_all_persons()

        # Отдельно для эксперта сделать оповещение, что он приглашён к участию в рассмотрении дела
        case_url = reverse('cases-detail', kwargs={'pk': self.case.pk})
        message = f'Вас запрошено у якості експерта до участі у розгляду справи ' \
                  f'<b><a href="{case_url}">{self.case.case_number}</a></b>'
        if self.case.expert == self.request.user:
            messages.add_message(self.request, messages.SUCCESS, message)
            self.notification_service.execute(message, [self.case.expert.pk])

    def _call_2002_actions(self):
        """Выполнение действий, характерных для стадии 2002 -
        "Здійснено розподіл колегії. Очікує на підписання розпорядження."."""
        case_change_stage_step(self.case.pk, 2002, self.request.user.pk)
        self.case.refresh_from_db()
        self.notify_all_persons()

        # Отдельно для членов коллегии сделать оповещение, что они входят в состав коллегии
        case_url = reverse('cases-detail', kwargs={'pk': self.case.pk})
        message = f'Ви були включені у склад колегії ' \
                  f'для розгляду справи <b><a href="{case_url}">{self.case.case_number}</a></b>'
        self.notification_service.execute(
            message,
            [item.person_id for item in self.case.collegiummembership_set.all()]
        )

    def _call_2003_actions(self):
        """Выполнение действий, характерных для стадии 2003 -
        "Розпорядження підписано. Очікує на прийняття до розгляду."."""
        # Изменение стадии дела
        case_change_stage_step(self.case.pk, 2003, self.request.user.pk)
        self.case.refresh_from_db()
        self.notify_all_persons()

    def _call_2004_actions(self):
        """Выполнение действий, характерных для стадии 2004 -
        "Документи для прийняття справи до розгляду очікують на підписання."."""
        # Изменение стадии дела
        case_change_stage_step(self.case.pk, 2004, self.request.user.pk)
        self.case.refresh_from_db()
        self.notify_all_persons()

    def _call_2005_actions(self):
        """Выполнение действий, характерных для стадии 2005 -
        "Документи для прийняття справи до розгляду очікують на підписання."."""
        # Изменение стадии дела
        case_change_stage_step(self.case.pk, 2005, self.request.user.pk)
        self.case.refresh_from_db()
        self.notify_all_persons()

        # Оповещение членов коллегии и секретаря о предварительном заседании
        case_url = reverse('cases-detail', kwargs={'pk': self.case.pk})
        message = f'Вас запрошено прийняти участь в підготовчому засіданні щодо' \
                  f'розгляду справи <b><a href="{case_url}">{self.case.case_number}</a>.</b>'
        persons = [item.person_id for item in self.case.collegiummembership_set.all()]
        persons.append(self.case.secretary_id)
        self.notification_service.execute(message, persons)

    def _call_2006_actions(self):
        """Выполнение действий, характерных для стадии 2005 -
        "Документи для прийняття справи до розгляду очікують на підписання."."""
        # Изменение стадии дела
        case_change_stage_step(self.case.pk, 2006, self.request.user.pk)
        self.case.refresh_from_db()
        self.notify_all_persons()

        # Оповещение членов коллегии и секретаря о необходимости подписания протокола о подготовительном заседании
        # case_url = reverse('cases-detail', kwargs={'pk': self.case.pk})
        # message = f'Вас запрошено прийняти участь в підготовчому засіданні щодо' \
        #           f'розгляду справи <b><a href="{case_url}">{self.case.case_number}</a>.</b>'
        # persons = [item.person_id for item in self.case.collegiummembership_set.all()]
        # persons.append(self.case.secretary_id)
        # self.notification_service.execute(message, persons)

    def _call_3000_actions(self):
        """Выполнение действий, характерных для стадии 3000 -
        "Справу прийнято до розгляду. Очікує на призначення засідання."."""
        # Изменение стадии дела
        case_change_stage_step(self.case.pk, 3000, self.request.user.pk)
        self.case.refresh_from_db()
        self.notify_all_persons()

    def _call_3001_actions(self):
        """Выполнение действий, характерных для стадии 3001 -
        "Створене засідання АП. Чекає на погодження членів колегії."."""
        # Изменение стадии дела
        case_change_stage_step(self.case.pk, 3001, self.request.user.pk)
        self.case.refresh_from_db()

        # Оповещение членов коллегии о приглашении к участии в заседании
        case_url = reverse('cases-detail', kwargs={'pk': self.case.pk})
        meetings_url = reverse('meetings-index')
        message = f'Вас запрошено прийняти участь в апеляційному засіданні щодо' \
                  f'розгляду справи <b><a href="{case_url}">{self.case.case_number}</a>.</b> ' \
                  f'Прийняти або відхилити запрошення можна на <a href="{meetings_url}">цій сторінці</a>.'
        self.notification_service.execute(
            message,
            [item.person_id for item in self.case.collegiummembership_set.all()]
        )

        # Оповещение людей, причастных к данному ап. делу, а также главы АП и его заместителей
        self.notify_all_persons()

    def _call_3002_actions(self):
        """Выполнение действий, характерных для стадии 3002 -
        "Створене засідання АП. Чекає на підписання документів."."""
        # Изменение стадии дела
        case_change_stage_step(self.case.pk, 3002, self.request.user.pk)
        self.case.refresh_from_db()

        # Оповещение людей, причастных к данному ап. делу, а также главы АП и его заместителей
        self.notify_all_persons()

        # Формирование документа "Повідомлення про засідання"
        case_create_docs(
            self.case.pk,
            [x['code'] for x in get_doc_types_for_meeting(self.case.claim.claim_kind_id)],
            self.request.user.pk,
            self.case.collegium_head.pk
        )
        self.notification_service.execute(
            'Вам передано на підпис документ.',
            [self.case.collegium_head.pk]
        )

    def _call_4000_actions(self):
        """Выполнение действий, характерных для стадии 4000 -
        "Чекає на проведення засідання Апеляційної палати."."""
        # Изменение стадии дела
        case_change_stage_step(self.case.pk, 4000, self.request.user.pk)
        self.case.refresh_from_db()
        self.notify_all_persons()

    def notify_all_persons(self):
        """Делает оповещение всех пользователей, которые причастны к делу,
        главы АП, заместителей, текущего пользователя."""
        # Оповещение пользователя, совершившего операцию, с помощью Django Messages
        message = self.get_message_stage()
        messages.add_message(self.request, messages.SUCCESS, message)

        # Оповещение людей, причастных к данному ап. делу, а также главы АП и его заместителей
        users_ids = case_get_all_persons(self.case.pk)
        self.notification_service.execute(message, users_ids)

    def get_message_stage(self):
        """Возвращает текст сообщения о смене стадии дела."""
        case_url = reverse('cases-detail', kwargs={'pk': self.case.pk})
        stage = CaseStageStep.objects.get(code=self.case.stage_step.code)
        message = f'Стадію справи <b><a href="{case_url}">{self.case.case_number}</a></b> ' \
                  f'змінено на <b>"{stage.title}"</b> (код стадії - {stage.code})'
        return message

    def execute(self):
        # Определение стадии
        case_stage_step = self.qualifier.get_stage_step(self.case)

        # Сравнение определённой стадии с текущей стадией, чтобы не предпринимать действия если они совпадают
        if self.case.stage_step.code != case_stage_step:
            # Вызов метода, выполняющего действия, которые необходимо выполнить на конкретной стадии ап. дела.
            stage_actions = {
                2000: self._call_2000_actions,
                2001: self._call_2001_actions,
                2002: self._call_2002_actions,
                2003: self._call_2003_actions,
                2004: self._call_2004_actions,
                2005: self._call_2005_actions,
                2006: self._call_2006_actions,
                3000: self._call_3000_actions,
                3001: self._call_3001_actions,
                3002: self._call_3002_actions,
                4000: self._call_4000_actions,
            }
            try:
                stage_actions[case_stage_step]()
                return case_stage_step
            except KeyError:
                pass

        return None
