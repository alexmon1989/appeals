from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property
from .managers import UserManager
from apps.common.models import TimeStampModel
from apps.classifiers.models import ObjKind


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    last_name = models.CharField("Прізвище", max_length=255, blank=True, null=True)
    first_name = models.CharField("Ім'я", max_length=255, blank=True, null=True)
    middle_name = models.CharField("По-батькові", max_length=255, blank=True, null=True)
    position = models.CharField("Посада", max_length=512, blank=True, null=True,
                                help_text='Вкажіть повну посаду із відділом, наприклад, '
                                          '"Начальник відділу забезпечення діяльності колегіальних '
                                          'органів Укрпатенту"')

    # Имя и должность в родительном падеже (может быть необходимо, например, при генерации документов)
    last_name_genitive = models.CharField("Прізвище у родовому відмінку", max_length=255, blank=True, null=True)
    first_name_genitive = models.CharField("Ім'я у родовому відмінку", max_length=255, blank=True, null=True)
    middle_name_genitive = models.CharField("По-батькові у родовому відмінку", max_length=255, blank=True, null=True)
    position_genitive = models.CharField("Посада у родовому відмінку", max_length=512, blank=True, null=True,
                                         help_text='Вкажіть повну посаду із відділом, наприклад, '
                                                   '"Начальнику відділу забезпечення діяльності колегіальних '
                                                   'органів Укрпатенту"')

    phone_number = models.CharField("Номер телефону", max_length=255, blank=True, null=True)
    specialities = models.ManyToManyField(ObjKind, blank=True, verbose_name='Спеціальності')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.email

    @cached_property
    def get_full_name(self) -> str:
        if self.last_name:
            return ('%s %s %s' % (self.last_name, self.first_name, self.middle_name)).strip()
        else:
            return self.certificateowner_set.first().pszSubjFullName.strip()

    def get_full_name_initials(self) -> str:
        return f"{self.last_name} {self.first_name[:1]}. {self.middle_name[:1]}."

    def get_full_name_genitive(self) -> str:
        """Возвращает ФИО пользователя в родительном падеже."""
        return f"{self.last_name_genitive} {self.first_name_genitive} {self.middle_name_genitive}"

    def get_full_name_initials_genitive(self) -> str:
        """Возвращает ФИО (имя и отчество - инициалы) пользователя в родительном падеже."""
        return f"{self.last_name_genitive} {self.first_name_genitive[:1]}. {self.middle_name_genitive[:1]}."

    def get_groups(self):
        groups = self.groups.values_list('name', flat=True)
        return ', '.join(groups)

    def belongs_to_group(self, group_name: str) -> bool:
        return self.groups.filter(name=group_name).exists()

    def belongs_to_groups(self, group_names: list) -> bool:
        return self.groups.filter(name__in=group_names).exists()

    @property
    def is_privileged(self) -> bool:
        """Привилегированный пользователь."""
        return self.is_superuser or self.belongs_to_groups(
            ['Голова апеляційної палати', 'Заступник голови апеляційної палати', 'Секретар']
        )

    @property
    def is_applicant(self) -> bool:
        """Заявитель."""
        return self.belongs_to_group('Заявник')

    @property
    def is_internal(self) -> bool:
        """Внутренний пользователь."""
        return not self.belongs_to_group('Заявник')

    @property
    def is_secretary(self) -> bool:
        """Секретарь."""
        return self.belongs_to_group('Секретар')


class CertificateOwner(TimeStampModel):
    """Модель данных владельца сертификата ЭЦП."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Користувач')
    pszIssuer = models.CharField('Ім’я ЦСК, що видав сертифікат', max_length=255, blank=True, null=True)
    pszIssuerCN = models.CharField('Реквізити ЦСК, що видав сертифікат', max_length=255, blank=True, null=True)
    pszSerial = models.CharField('Реєстраційний номер сертифіката', max_length=255, blank=True, null=True)
    pszSubject = models.CharField('Ім’я власника сертифіката', max_length=255, blank=True, null=True)
    pszSubjCN = models.CharField('Реквізити власника сертифіката', max_length=255, blank=True, null=True)
    pszSubjOrg = models.CharField('Організація до якої належить власник сертифіката', max_length=255, blank=True,
                                  null=True)
    pszSubjOrgUnit = models.CharField('Підрозділ організації до якої належить власник сертифіката', max_length=255,
                                      blank=True, null=True)
    pszSubjTitle = models.CharField('Посада власника сертифіката', max_length=255, blank=True, null=True)
    pszSubjState = models.CharField('Назва області до якої належить власник сертифіката', max_length=255, blank=True,
                                    null=True)
    pszSubjFullName = models.CharField('Повне ім’я власника сертифіката', max_length=255, blank=True, null=True)
    pszSubjAddress = models.CharField('Адреса власника сертифіката', max_length=255, blank=True, null=True)
    pszSubjPhone = models.CharField('Номер телефону власника сертифіката', max_length=255, blank=True, null=True)
    pszSubjEMail = models.CharField('Адреса електронної пошти власника сертифіката', max_length=255, blank=True,
                                    null=True)
    pszSubjDNS = models.CharField('DNS-ім`я чи інше технічного засобу', max_length=255, blank=True, null=True)
    pszSubjEDRPOUCode = models.CharField('Код ЄДРПОУ власника сертифіката', max_length=255, blank=True, null=True)
    pszSubjDRFOCode = models.CharField('Код ДРФО власника сертифіката', max_length=255, blank=True, null=True)
    pszSubjLocality = models.CharField('Locality власника сертифіката', max_length=255, blank=True, null=True)

    def __str__(self):
        return self.pszSerial

    def save(self, *args, **kwargs):
        """Переопределение метода сохранения модели."""
        super().save(*args, **kwargs)
        # Создание нового пользователя
        if not self.user:
            email = self.pszSubjDRFOCode or self.pszSubjEDRPOUCode
            user, created = User.objects.get_or_create(email=email)
            self.user = user
            self.save()

            # Добавление его в группу заявителей
            group = Group.objects.get(name='Заявник')
            user.groups.add(group)

    class Meta:
        verbose_name = 'Сертифікат'
        verbose_name_plural = 'Сертифікати'
