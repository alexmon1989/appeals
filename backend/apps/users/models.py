from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property
from .managers import UserManager
from backend.core.models import TimeStampModel


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    last_name = models.CharField("Прізвище", max_length=255, blank=True, null=True)
    first_name = models.CharField("Ім'я", max_length=255, blank=True, null=True)
    middle_name = models.CharField("По-батькові", max_length=255, blank=True, null=True)
    phone_number = models.CharField("Номер телефону", max_length=255, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.email

    @cached_property
    def get_full_name(self):
        if self.belongs_to_group('Заявник'):
            return self.certificateowner.pszSubjFullName
        else:
            full_name = '%s %s %s' % (self.last_name, self.first_name, self.middle_name)
        return full_name.strip()

    def get_groups(self):
        groups = self.groups.values_list('name', flat=True)
        return ', '.join(groups)

    def belongs_to_group(self, group_name: str) -> bool:
        return self.groups.filter(name=group_name).exists()

    @property
    def is_privileged(self) -> bool:
        """Привилегированный пользователь."""
        return self.is_superuser and self.belongs_to_group('Голова апеляційної палати')

    @property
    def is_applicant(self) -> bool:
        """Привилегированный пользователь."""
        return self.belongs_to_group('Заявник')


class CertificateOwner(TimeStampModel):
    """Модель данных владельца сертификата ЭЦП."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Користувач')
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
            user, created = User.objects.get_or_create(email=self.pszSerial)
            self.user = user
            self.save()

            # Добавление его в группу заявителей
            group = Group.objects.get(name='Заявник')
            user.groups.add(group)

    class Meta:
        verbose_name = 'Сертифікат'
        verbose_name_plural = 'Сертифікати'
