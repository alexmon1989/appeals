from typing import Iterable

from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.cases.models import Case, CaseStageStep
from .case_services import case_change_stage_step, case_get_all_persons_for_notifying

from apps.notifications.services import Notifier, MultipleUsersNotifier


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
            for document in self.case.document_set.all():
                # Документ "Розпорядження про створення колегії" существует и подписан главой комиссии
                if document.document_type.code == '0005' and document.is_signed_by_head:
                    return True
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
    def __init__(self, qualifier: CaseStageStepQualifier, case: Case, user: UserModel,
                 current_user_notifiers: Iterable[Notifier] = None,
                 multiple_user_notifiers: Iterable[MultipleUsersNotifier] = None):
        self.case = case
        self.qualifier = qualifier
        self.user = user
        self.current_user_notifiers = current_user_notifiers or []
        self.multiple_user_notifiers = multiple_user_notifiers or []

    def _call_2000_actions(self):
        """Выполнение действий, характерных для стадии 2000 -
        "Прийнято в роботу. Очікує на заповнення досьє."."""
        self.case.secretary = self.user
        self.case.save()
        case_change_stage_step(self.case.pk, 2000, self.user.pk)
        self.case.refresh_from_db()
        self.notify_all_persons()

        # Отдельно для секретаря сделать оповещение, что его назначено секретарём по делу
        # Текущий пользователь и есть секретарь, т.к. данную операцию проводит только пользователь с ролью секретарь
        case_url = reverse('cases-detail', kwargs={'pk': self.case.pk})
        message = f'Вас призначено секретарем по справі <b><a href="{case_url}">{self.case.case_number}</a></b>'
        for notifier in self.current_user_notifiers:
            notifier.notify(message, 'success')
        for notifier in self.multiple_user_notifiers:
            notifier.set_addressees([self.user])
            notifier.notify(message, 'success')

    def _call_2001_actions(self):
        """Выполнение действий, характерных для стадии 2001 -
        "Досьє заповнено. Очікує на розподіл колегії."."""
        case_change_stage_step(self.case.pk, 2001, self.user.pk)
        self.case.refresh_from_db()
        self.notify_all_persons()

        # Отдельно для эксперта сделать оповещение, что он приглашён к участию в рассмотрении дела
        case_url = reverse('cases-detail', kwargs={'pk': self.case.pk})
        message = f'Вас запрошено у якості експерта до участі у розгляду справи ' \
                  f'<b><a href="{case_url}">{self.case.case_number}</a></b>'
        if self.case.expert == self.user:
            for notifier in self.current_user_notifiers:
                notifier.notify(message, 'success')
        for notifier in self.multiple_user_notifiers:
            notifier.set_addressees([self.case.expert])
            notifier.notify(message, 'success')

    def _call_2002_actions(self):
        """Выполнение действий, характерных для стадии 2002 -
        "Здійснено розподіл колегії. Очікує на підписання розпорядження."."""
        case_change_stage_step(self.case.pk, 2002, self.user.pk)
        self.case.refresh_from_db()
        self.notify_all_persons()

        # Отдельно для членов коллегии сделать оповещение, что они входят в состав коллегии
        case_url = reverse('cases-detail', kwargs={'pk': self.case.pk})
        message = f'Ви були включені у склад колегії ' \
                  f'для розгляду справи <b><a href="{case_url}">{self.case.case_number}</a></b>'
        for notifier in self.multiple_user_notifiers:
            users = []
            for item in self.case.collegiummembership_set.all():
                users.append(item.person)
            notifier.set_addressees(users)
            notifier.notify(message, 'success')

        # TODO: уведомление подписанту, что ему на подписание передано документ

    def _call_2003_actions(self):
        """Выполнение действий, характерных для стадии 2003 -
        "Розпорядження підписано. Очікує на прийняття до розгляду."."""
        # Изменение стадии дела
        case_change_stage_step(self.case.pk, 2003, self.user.pk)
        self.case.refresh_from_db()
        self.notify_all_persons()

    def notify_all_persons(self):
        """Делает оповещение всех пользователей, которые причастны к делу,
        главы АП, заместителей, текущего пользователя."""
        # Оповещение пользователя, совершившего операцию
        message = self.get_message_stage()
        for notifier in self.current_user_notifiers:
            notifier.notify(message, 'success')

        # Оповещение людей, причастных к данному ап. делу, а также главы АП и его заместителей
        addressees = case_get_all_persons_for_notifying(self.case.pk)
        for notifier in self.multiple_user_notifiers:
            notifier.set_addressees(addressees)
            notifier.notify(message, 'success')

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
            }
            try:
                stage_actions[case_stage_step]()
                return case_stage_step
            except KeyError:
                pass

        return None
