from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from ...models import Case
from ....classifiers.models import ClaimKind, ObjKind

from random import randint, sample
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Creates test data for testing'
    users = []

    def create_users(self):
        # Создание пользователей всех ролей
        possible_last_names = (
            'Мельник',
            'Шевченко',
            'Коваленко',
            'Бондаренко',
            'Бойко',
            'Ткаченко',
            'Кравченко',
            'Ковальчук',
            'Коваль',
            'Олійник',
        )

        possible_first_names = (
            'Олександр',
            'Сергій',
            'Тарас',
            'Дмитро',
            'Максим',
            'Іван',
            'Петро',
            'Євген',
            'Микола',
            'Анатолій',
        )

        possible_middle_names = (
            'Олександрович',
            'Сергійович',
            'Тарасович',
            'Дмитрович',
            'Максимович',
            'Іванович',
            'Петрович',
            'Євгенович',
            'Миколайович',
            'Анатолійович',
        )

        User = get_user_model()

        users = {
            'head': None,
            'members': [],
            'experts': [],
        }
        # Создание пользователя с группой "Голова апеляційної палати"
        user = User.objects.create_user(email='head@ukrpatent.org', password='123456')
        user.last_name = possible_last_names[randint(0, len(possible_last_names)-1)]
        user.first_name = possible_first_names[randint(0, len(possible_first_names)-1)]
        user.middle_name = possible_middle_names[randint(0, len(possible_middle_names)-1)]
        user.save()

        group = Group.objects.get(name='Голова апеляційної палати')
        user.groups.add(group)
        users['head'] = user

        # Создание пользователей с группой "Члени апеляційної палати"
        for i in range(10):
            user = User.objects.create_user(email=f"member_{i}@ukrpatent.org", password='123456')
            user.last_name = possible_last_names[randint(0, len(possible_last_names)-1)]
            user.first_name = possible_first_names[randint(0, len(possible_first_names)-1)]
            user.middle_name = possible_middle_names[randint(0, len(possible_middle_names)-1)]
            user.save()

            group = Group.objects.get(name='Члени апеляційної палати')
            user.groups.add(group)
            users['members'].append(user)

        # Создание пользователей с группой "Третя особа"
        for i in range(10):
            user = User.objects.create_user(email=f"expert_{i}@ukrpatent.org", password='123456')
            user.last_name = possible_last_names[randint(0, len(possible_last_names)-1)]
            user.first_name = possible_first_names[randint(0, len(possible_first_names)-1)]
            user.middle_name = possible_middle_names[randint(0, len(possible_middle_names)-1)]
            user.save()

            group = Group.objects.get(name='Третя особа')
            user.groups.add(group)
            users['experts'].append(user)

        self.users = users

    def create_cases(self):
        """Создаёт апеляционные дела"""
        obj_kinds = ObjKind.objects.all()
        claim_kinds = ClaimKind.objects.all()

        now = datetime.now()

        for i in range(50):
            deadline = self.random_date(now + timedelta(days=30), now + timedelta(days=90))
            hearing = self.random_date(deadline - timedelta(days=7), deadline - timedelta(days=1)) if randint(0, 1) else None

            case = Case.objects.create(
                case_number=f"{str(i).zfill(4)}/2022",
                app_number=randint(100000000, 9999999999),
                obj_kind=obj_kinds[randint(0, obj_kinds.count() - 1)],
                claim_kind=claim_kinds[randint(0, claim_kinds.count() - 1)],
                obj_title=f"Назва об'єкту {i}",
                applicant_name=f"Заявник {randint(1, 20)}",
                applicant_represent=f"Представник {randint(1, 10)}",
                mailing_address=f"Адреса {i}",
                claim_date=self.random_date(now - timedelta(days=7), now),
                deadline=deadline,
                hearing=hearing,
            )
            case.save()

            # Члены коллегии - глава + 3 обычных члена комиссии
            case.collegium.add(self.users['head'])
            member_ids = sample(range(1, len(self.users['members'])-1), 3)
            for j in member_ids:
                case.collegium.add(self.users['members'][j])
            case.secretary = self.users['members'][member_ids[1]]
            case.papers_owner = self.users['members'][member_ids[1]]
            case.expert = self.users['experts'][randint(0, len(self.users['experts'])-1)]
            case.save()

    def random_date(self, start, end):
        """Generate a random datetime between `start` and `end`"""
        return start + timedelta(
            # Get a random amount of seconds between `start` and `end`
            seconds=randint(0, int((end - start).total_seconds())),
        )

    def handle(self, *args, **options):
        self.stdout.write('Створення користувачів...')
        self.create_users()
        self.stdout.write('Створення апеляційних справ...')
        self.create_cases()

        self.stdout.write(self.style.SUCCESS('Finished'))
