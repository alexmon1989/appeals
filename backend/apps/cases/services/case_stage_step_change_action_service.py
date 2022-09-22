from typing import Iterable

from django.contrib.auth import get_user_model

from apps.cases.models import Case
from .case_services import case_change_stage_step, case_get_all_persons_for_notifying

from apps.notifications.services import Notifier, MultipleUsersNotifier


UserModel = get_user_model()


class CaseStageStepQualifier:
    """Класс, задачей которого есть определить фактическую стадию ап. дела (например, по подписанным документам)."""
    case: Case

    def _satisfies_2003(self):
        """Удовлетворяет условиям стадии 2003 "Розпорядження підписано. Очікує на прийняття до розгляду."."""
        for document in self.case.document_set.all():
            # Документ "Розпорядження про створення колегії" существует и подписан главой комиссии
            if document.document_type.code == '0005' and document.is_signed_by_head:
                return True
        return False

    def get_stage_step(self, case: Case) -> int:
        self.case = case
        if self._satisfies_2003():
            return 2003
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

    def _call_2003_actions(self):
        """Выполнение действий, характерных для стадии 2003 -
        "Розпорядження підписано. Очікує на прийняття до розгляду."."""
        # Изменение стадии дела
        case_change_stage_step(self.case.pk, 2003, self.user.pk)

        # Оповещение пользователя, совершившего операцию
        message = 'Стадію справи змінено на <b>' \
                  '"Розпорядження підписано. Очікує на прийняття до розгляду."</b> (код стадії - 2003)'
        for notifier in self.current_user_notifiers:
            notifier.notify(message, 'success')

        # Оповещение людей, причастных к данному ап. делу, а также главы АП и его заместителей
        addressees = case_get_all_persons_for_notifying(self.case.pk)
        for notifier in self.multiple_user_notifiers:
            notifier.set_addressees(addressees)
            notifier.notify(message, 'success')

    def execute(self):
        # Определение стадии
        case_stage_step = self.qualifier.get_stage_step(self.case)

        # Сравнение определённой стадии с текущей стадией, чтобы не предпринимать действия если они совпадают
        if self.case.stage_step.code != case_stage_step:
            # Вызов метода, выполняющего действия, которые необходимо выполнить на конкретной стадии ап. дела.
            stage_actions = {
                2003: self._call_2003_actions
            }
            try:
                stage_actions[case_stage_step]()
            except KeyError:
                pass
