from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from ...models import Case, CollegiumMembership
from ....classifiers.models import ClaimKind, ObjKind

from random import randint, sample
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Creates test data'
    users = []

    def create_users(self):
        staff = [
            {
                'last_name': 'Василенко',
                'first_name': 'Марія',
                'middle_name': 'Олександрівна',
                'email': 'm.vasilenko@ukrpatent.org',
                'position': 'Директор з питань права та адміністрування державних реєстрів, '
                            'начальник відділення правового забезпечення інтелектуальної власності '
                            'державного підприємства  “Український інститут інтелектуальної власності”,'
                            ' голова Апеляційної палати',
                'groups': ['Голова Апеляційної палати', ],
                'specialities': ['Промисловий зразок', 'Торговельна марка', 'Географічне зазначення'],
            },
            {
                'last_name': 'Шатова',
                'first_name': 'Інна',
                'middle_name': 'Олексіївна',
                'email': 'ishatova@me.gov.ua',
                'position': 'Заступник начальника управління промислової власності – начальник відділу права '
                            'промислової власності департаменту розвитку сфери інтелектуальної власності Мінекономіки, '
                            'заступник голови Апеляційної палати',
                'groups': ['Заступник голови Апеляційної палати', ],
                'specialities': ['Винахід', 'Корисна модель', 'Промисловий зразок', 'Торговельна марка', 'Географічне зазначення'],
            },
            {
                'last_name': 'Жмурко',
                'first_name': 'Оксана',
                'middle_name': 'Василівна',
                'email': 'o.zhmurko@ukrpatent.org',
                'position': 'Начальник відділу розгляду звернень державного підприємства '
                            '“Український інститут інтелектуальної власності”, заступник голови Апеляційної палати',
                'groups': ['Заступник голови Апеляційної палати', ],
                'specialities': ['Промисловий зразок', 'Торговельна марка', 'Географічне зазначення'],
            },
            {
                'last_name': 'БАХМАЧ',
                'first_name': 'Євгенія',
                'middle_name': 'Валентинівна',
                'email': 'e.bakhmach@ukrpatent.org',
                'position': 'Заступник начальника відділу хіміко-біологічних технологій '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Винахід', 'Корисна модель', ],
            },
            {
                'last_name': 'БУРМІСТРОВА',
                'first_name': 'Наталія',
                'middle_name': 'Григорівна',
                'email': 'n.burmistrova@ukrpatent.org',
                'position': 'Професіонал з інтелектуальної власності 2-ї категорії відділу розгляду звернень '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Промисловий зразок', 'Торговельна марка', 'Географічне зазначення'],
            },
            {
                'last_name': 'ВИХОВАНЕЦЬ',
                'first_name': 'Ірина',
                'middle_name': 'Вікторівна',
                'email': 'i.vykhovanets@ukrpatent.org',
                'position': 'Провідний експерт сектору електротехніки та приладобудування відділу фізико-технічних '
                            'технологій державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Винахід', 'Корисна модель', ],
            },
            {
                'last_name': 'ГАЙДУК',
                'first_name': 'Валентина',
                'middle_name': 'Володимирівна',
                'email': 'v.gayduk@ukrpatent.org',
                'position': 'Начальник відділу прав на позначення '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Промисловий зразок', 'Торговельна марка', 'Географічне зазначення'],
            },
            {
                'last_name': 'ГОВОРУХА',
                'first_name': 'Марина',
                'middle_name': 'Олександрівна',
                'email': 'm.govoruha@ukrpatent.org',
                'position': 'Провідний експерт відділу будівельної та '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Винахід', 'Корисна модель', ],
            },
            {
                'last_name': 'ГОРБИК',
                'first_name': 'Юлія',
                'middle_name': 'Анатоліївна',
                'email': 'j.gorbic@ukrpatent.org',
                'position': 'Заступник начальника відділу розгляду '
                            'звернень державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Промисловий зразок', 'Торговельна марка', 'Географічне зазначення'],
            },
            {
                'last_name': 'ГОСТЄВА',
                'first_name': 'Анна',
                'middle_name': 'Іванівна',
                'email': 'a.gostieva@ukrpatent.org',
                'position': 'Професіонал з інтелектуальної власності 2-ї категорії відділу розгляду звернень '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Промисловий зразок', 'Торговельна марка', 'Географічне зазначення'],
            },
            {
                'last_name': 'ГРОМОВА',
                'first_name': 'Юлія',
                'middle_name': 'Валеріївна',
                'email': 'j.gromova@ukrpatent.org',
                'position': 'Професіонал з інтелектуальної власності відділу прав на позначення '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Промисловий зразок', 'Торговельна марка', 'Географічне зазначення'],
            },
            {
                'last_name': 'ДАНИЛОВА',
                'first_name': 'Олена',
                'middle_name': 'Вікторівна',
                'email': 'o.danilova@ukrpatent.org',
                'position': 'Начальник відділу контролю якості та удосконалення експертизи '
                            'заявок на винаходи, корисні моделі та ТІМ '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Винахід', 'Корисна модель', ],
            },
            {
                'last_name': 'ДІДУШКО',
                'first_name': 'Ірина',
                'middle_name': 'Олегівна',
                'email': 'i.didushko@ukrpatent.org',
                'position': 'Професіонал з інтелектуальної власності 1-ї категорії відділу прав на позначення '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Промисловий зразок', 'Географічне зазначення'],
            },
            {
                'last_name': 'КОЗЕЛЕЦЬКА',
                'first_name': 'Наталія',
                'middle_name': 'Олександрівна',
                'email': 'n.kozeletska@ukrpatent.org',
                'position': 'Професіонал з інтелектуальної власності 1-ї категорії відділу сприяння захисту прав '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Промисловий зразок', 'Торговельна марка', 'Географічне зазначення'],
            },
            {
                'last_name': 'КОТИК',
                'first_name': 'Катерина',
                'middle_name': 'Олександрівна',
                'email': 'k.kotik@ukrpatent.org',
                'position': 'Провідний експерт відділу контролю якості та удосконалення експертизи заявок на винаходи, '
                            'корисні моделі та топографії інтегральних мікросхем '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Винахід', 'Корисна модель', ],
            },
            {
                'last_name': 'КРАМАР',
                'first_name': 'Іван',
                'middle_name': 'Анатолійович',
                'email': 'i.kramar@ukrpatent.org',
                'position': 'Провідний експерт відділу контролю якості та удосконалення експертизи заявок '
                            'на винаходи, корисні моделі та ТІМ '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Винахід', 'Корисна модель', ],
            },
            {
                'last_name': 'КРАСОВСЬКИЙ',
                'first_name': 'Віталій',
                'middle_name': 'Григорович',
                'email': 'krasovsky@ukrpatent.org',
                'position': 'Професіонал з інтелектуальної власності 1-ї категорії відділу розгляду звернень '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Промисловий зразок', 'Торговельна марка', 'Географічне зазначення'],
            },
            {
                'last_name': 'КУРНОСОВА',
                'first_name': 'Світлана',
                'middle_name': 'Володимирівна',
                'email': 's.kurnosova@ukrpatent.org',
                'position': 'Провідний експерт відділу фізико-технічних технологій '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Винахід', 'Корисна модель', ],
            },
            {
                'last_name': 'КУХАРЕНКО',
                'first_name': 'Хельга',
                'middle_name': 'Василівна',
                'email': 'kuharenko@ukrpatent.org',
                'position': 'Провідний експерт відділу фізико-технічних технологій '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Винахід', 'Корисна модель', ],
            },
            {
                'last_name': 'ПАВЛОВ',
                'first_name': 'Дмитро',
                'middle_name': 'Олегович',
                'email': 'dmitry_pavlov@ukrpatent.org',
                'position': 'Начальник відділу прав на результати науково-технічної діяльності '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Винахід', 'Корисна модель', 'Промисловий зразок',],
            },
            {
                'last_name': 'ПАДУЧАК',
                'first_name': 'Богдан',
                'middle_name': 'Михайлович',
                'email': 'bpaduchak@me.gov.ua',
                'position': 'Заступник директора департаменту розвитку сфери інтелектуальної власності – '
                            'начальник управління промислової власності Мінекономіки (за згодою)',
                'groups': ['Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Промисловий зразок', 'Торговельна марка', 'Географічне зазначення'],
            },
            {
                'last_name': 'ПОЛОНСЬКА',
                'first_name': 'Тетяна',
                'middle_name': 'Михайлівна',
                'email': 't.polonska@ukrpatent.org',
                'position': 'Провідний експерт відділу хіміко-біологічних технологій '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Винахід', 'Корисна модель', ],
            },
            {
                'last_name': 'ПОЛІЩУК',
                'first_name': 'Наталія',
                'middle_name': 'Володимирівна',
                'email': 'n.polishchuk@ukrpatent.org',
                'position': 'Професіонал з інтелектуальної власності 1-ї категорії відділу сприяння захисту прав '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Промисловий зразок', 'Торговельна марка', 'Географічне зазначення'],
            },
            {
                'last_name': 'САЛАМОВ',
                'first_name': 'Олександр',
                'middle_name': 'Володимирович',
                'email': 'salamov@ukrpatent.org',
                'position': 'Професіонал з інтелектуальної власності 1-ї категорії відділу сприяння захисту прав '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Промисловий зразок', 'Торговельна марка', 'Географічне зазначення'],
            },
            {
                'last_name': 'САЛФЕТНИК',
                'first_name': 'Тетяна',
                'middle_name': 'Петрівна',
                'email': 'tatyana_salfetnik@ukrpatent.org',
                'position': 'Професіонал з інтелектуальної власності 2-ї категорії відділу розгляду звернень '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Промисловий зразок', 'Торговельна марка', 'Географічне зазначення'],
            },
            {
                'last_name': 'СТОРОЖИК',
                'first_name': 'Людмила',
                'middle_name': 'Анатоліївна',
                'email': 'storoguk@ukrpatent.org',
                'position': 'Заступник начальника відділу фізико-хімічних технологій '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Винахід', 'Корисна модель', ],
            },
            {
                'last_name': 'ТЕРЕХОВА',
                'first_name': 'Тетяна',
                'middle_name': 'В\'ячеславівна',
                'email': 't.terehova@ukrpatent.org',
                'position': 'Заступник начальника відділу прав на позначення '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Торговельна марка', 'Географічне зазначення'],
            },
            {
                'last_name': 'ТУМКО',
                'first_name': 'Лариса',
                'middle_name': 'Іванівна',
                'email': 'l.tumko@ukrpatent.org',
                'position': 'Заступник начальника відділу прав на результати науково-технічної діяльності '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Промисловий зразок', ],
            },
            {
                'last_name': 'ФІНАГІНА',
                'first_name': 'Владлєна',
                'middle_name': 'Борисівна',
                'email': 'v.finagina@ukrpatent.org',
                'position': 'Професіонал з інтелектуальної власності 1-ї категорії відділу сприяння захисту прав '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Промисловий зразок', 'Торговельна марка', 'Географічне зазначення'],
            },
            {
                'last_name': 'ЦИБЕНКО',
                'first_name': 'Людмила',
                'middle_name': 'Андріївна',
                'email': 'tsybenko@ukrpatent.org',
                'position': 'Професіонал з інтелектуальної власності 2-ї категорії відділу розгляду звернень '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Торговельна марка', 'Географічне зазначення'],
            },
            {
                'last_name': 'ЧЕРНЕЦЬКА',
                'first_name': 'Наталія',
                'middle_name': 'Миколаївна',
                'email': 'n.chernetska@ukrpatent.org',
                'position': 'Заступник начальника відділу хімії та фармацевтики '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Винахід', 'Корисна модель', ],
            },
            {
                'last_name': 'ЧУЯН',
                'first_name': 'Юрій',
                'middle_name': 'Володимирович',
                'email': 'y.chuyan@ukrpatent.org',
                'position': 'Провідний експерт відділу фізико-технічних технологій '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Винахід', 'Корисна модель', ],
            },
            {
                'last_name': 'ШЕКА',
                'first_name': 'Олена',
                'middle_name': 'Петрівна',
                'email': 'e.sheka@ukrpatent.org',
                'position': 'Провідний експерт відділу будівельної та гірничої справи '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Винахід', 'Корисна модель', ],
            },
            {
                'last_name': 'ШУМІЛОВА',
                'first_name': 'Лідія',
                'middle_name': 'Дмитрівна',
                'email': 'L.shumilova@iii.ua',
                'position': 'Начальник відділення патентно-інформаційних послуг, консультацій '
                            'та сприяння інноваційній діяльності '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Винахід', 'Корисна модель', 'Промисловий зразок', 'Торговельна марка', 'Географічне зазначення'],
            },

            {
                'last_name': 'Рябухін',
                'first_name': 'Євген',
                'middle_name': 'Михайлович',
                'email': 'e.ryabuhin@ukrpatent.org',
                'position': 'Провідний експерт відділу інженерних технологій '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Експерт', ],
                'specialities': ['Винахід', 'Корисна модель', 'Промисловий зразок', 'Торговельна марка', 'Географічне зазначення'],
            },
            {
                'last_name': 'КОЛОМІЄЦЬ',
                'first_name': 'Олексій',
                'middle_name': 'Володимирович',
                'email': 'o.kolomiiets@ukrpatent.org',
                'position': 'Провідний експерт відділу інженерних технологій '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Експерт', ],
                'specialities': ['Винахід', 'Корисна модель', 'Промисловий зразок', 'Торговельна марка', 'Географічне зазначення'],
            },

            {
                'last_name': 'Монастирецький',
                'first_name': 'Олександр',
                'middle_name': 'Миколайович',
                'email': 'a.monastyretsky@ukrpatent.org',
                'position': 'Аналітик комп\'ютерних систем 1 категорії відділу системного аналізу та технологічного забезпечення '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Голова апеляційної палати', 'Заступник голови апеляційної палати', 'Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Винахід', 'Корисна модель', 'Промисловий зразок', 'Торговельна марка', 'Географічне зазначення'],
                'is_superuser': True,
                'is_staff': True,
            },
            {
                'last_name': 'Пустовіт',
                'first_name': 'Тарас',
                'middle_name': 'Сергійович',
                'email': 'taras@ukrpatent.org',
                'position': 'Начальник управління комп\'ютеризації та інформаційних технологій '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Голова апеляційної палати', 'Заступник голови апеляційної палати', 'Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Винахід', 'Корисна модель', 'Промисловий зразок', 'Торговельна марка', 'Географічне зазначення'],
                'is_superuser': True,
                'is_staff': True,
            },
            {
                'last_name': 'Болєлий',
                'first_name': 'Сергій',
                'middle_name': 'Миколайович',
                'email': 's.bolelyi@ukrpatent.org',
                'position': 'Заступник начальника відділу системного аналізу та технологічного забезпечення '
                            'державного підприємства “Український інститут інтелектуальної власності”',
                'groups': ['Голова апеляційної палати', 'Заступник голови апеляційної палати', 'Член Апеляційної палати', 'Секретар', ],
                'specialities': ['Винахід', 'Корисна модель', 'Промисловий зразок', 'Торговельна марка', 'Географічне зазначення'],
                'is_superuser': True,
                'is_staff': True,
            },
        ]

        User = get_user_model()

        User.objects.all().delete()

        c = len(staff)
        i = 1
        print('Users creating...')
        for user_data in staff:
            user = User.objects.create_user(email=user_data['email'], password='123456')
            user.last_name = user_data['last_name'].lower().capitalize()
            user.first_name = user_data['first_name']
            user.middle_name = user_data['middle_name']
            user.position = user_data['position']
            user.is_superuser = user_data.get('is_superuser', False)
            user.is_staff = user_data.get('is_staff', False)
            user.save()

            for group in user_data['groups']:
                g, created = Group.objects.get_or_create(name=group)
                user.groups.add(g)

            for speciality in user_data['specialities']:
                obj_kind = ObjKind.objects.get(title=speciality)
                user.specialities.add(obj_kind)

            print(f"created {i}/{c}")
            i += 1


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

            # Члены коллегии - 3 обычных члена комиссии
            # case.collegium.add(self.users['head'])
            member_keys = sample(range(1, len(self.users['members'])-1), 3)
            for j, key in enumerate(member_keys):
                if j == 0:
                    CollegiumMembership.objects.create(person=self.users['members'][key], case=case, is_head=True)
                else:
                    CollegiumMembership.objects.create(person=self.users['members'][key], case=case, is_head=False)
            case.secretary = self.users['members'][member_keys[1]]
            case.papers_owner = self.users['members'][member_keys[1]]
            case.expert = self.users['experts'][randint(0, len(self.users['experts'])-1)]
            case.save()

    def random_date(self, start, end):
        """Generate a random datetime between `start` and `end`"""
        return start + timedelta(
            # Get a random amount of seconds between `start` and `end`
            seconds=randint(0, int((end - start).total_seconds())),
        )

    def handle(self, *args, **options):
        self.create_users()
        # self.stdout.write('Створення апеляційних справ...')
        # self.create_cases()

        self.stdout.write(self.style.SUCCESS('Finished'))
