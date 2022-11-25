from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Prefetch, Count, Q, Case, When
from django.db.models.functions import Concat
from django.utils import timezone

from .models import CertificateOwner, User
from apps.classifiers.models import ObjKind

from typing import Iterable
import os
import json
import logging

logger = logging.getLogger(__name__)


UserModel = get_user_model()


def set_key_center_settings(eu_interface, key_center):
    """Устанавливает параметры соединения с АЦСК"""
    eu_interface.Initialize()
    ca_settings = {
        'szPath': settings.EUSIGN_FILESTORE_PATH,
        'bCheckCRLs': True,
        'bAutoRefresh': True,
        'bOwnCRLsOnly': True,
        'bFullAndDeltaCRLs': True,
        'bAutoDownloadCRLs': True,
        'bSaveLoadedCerts': True,
        'dwExpireTime': 3600,
    }
    eu_interface.SetFileStoreSettings(ca_settings)

    ocspAccessPointAddress = key_center.get('ocspAccessPointAddress', '')
    ca_settings = {
        'bUseOCSP': ocspAccessPointAddress != '',
        'szAddress': ocspAccessPointAddress,
        'bBeforeStore': True,
        'szPort': str(key_center['ocspAccessPointPort']),
    }
    eu_interface.SetOCSPSettings(ca_settings)

    tspAddress = key_center.get('tspAddress')
    ca_settings = {
        'bGetStamps': tspAddress != '',
        'szAddress': tspAddress,
        'szPort': str(key_center.get('tspAddressPort', '')),
    }
    eu_interface.SetTSPSettings(ca_settings)

    cmpAddress = key_center.get('cmpAddress', '')
    ca_settings = {
        'bUseCMP': cmpAddress != '',
        'szAddress': cmpAddress,
        'szPort': '80',
        'szCommonName': '',
    }
    eu_interface.SetCMPSettings(ca_settings)


def get_signed_data_info(signed_data, secret, key_center_title):
    """Проверяет валидность ЭЦП."""
    # Загрузка бибилиотек ІІТ
    from EUSignCP import EULoad, EUGetInterface, EUGetInterface, EUUnload

    EULoad()
    pIface = EUGetInterface()
    pIface.Initialize()
    eu_interface = EUGetInterface()

    # Считывание настроек центров сертификации из файла CAs.json
    key_centers = open(os.path.join(settings.BASE_DIR, 'apps', 'my_auth', 'static', 'my_auth', 'CAs.json'), "r").read()
    key_centers = json.loads(key_centers)

    # Применение настроек центра сертификации
    for key_center in key_centers:
        if key_center_title in key_center['issuerCNs']:
            set_key_center_settings(eu_interface, key_center)
            break

    # Проверка подписи
    pData = secret.encode('utf-16-le')
    signed_data = signed_data.encode()
    sign_info = {}
    try:
        # Верификация и получение данных из подписанных данных
        pIface.VerifyData(pData, len(pData), signed_data, None, len(signed_data), sign_info)
    except Exception as e:
        print(e)
        # logger.error(e)

    # Выгрузка бибилиотек ІІТ
    eu_interface.Finalize()
    EUUnload()

    return sign_info


def get_certificate(post_data, secret):
    """Возвращает сертификат ЭЦП."""
    if settings.VALIDATE_DS and not post_data['serial'] in settings.VALIDATE_DS_WHITE_LIST_CERTS:
        # Проверка валидности ЭЦП
        sign_info = get_signed_data_info(post_data['signed_data'],
                                         secret,
                                         post_data['key_center_title'])
        if not sign_info:
            # Проверка закончилась неудачей
            return None
        else:
            try:
                cert = CertificateOwner.objects.get(pszSerial=sign_info['pszSerial'])
            except CertificateOwner.DoesNotExist:
                # Запись данных ключа в БД
                cert = CertificateOwner(
                    pszIssuer=sign_info.get('pszIssuer'),
                    pszIssuerCN=sign_info.get('pszIssuerCN'),
                    pszSerial=sign_info.get('pszSerial'),
                    pszSubject=sign_info.get('pszSubject'),
                    pszSubjCN=sign_info.get('pszSubjCN'),
                    pszSubjOrg=sign_info.get('pszSubjOrg'),
                    pszSubjOrgUnit=sign_info.get('pszSubjOrgUnit'),
                    pszSubjTitle=sign_info.get('pszSubjTitle'),
                    pszSubjState=sign_info.get('pszSubjState'),
                    pszSubjFullName=sign_info.get('pszSubjFullName'),
                    pszSubjAddress=sign_info.get('pszSubjAddress'),
                    pszSubjPhone=sign_info.get('pszSubjPhone'),
                    pszSubjEMail=sign_info.get('pszSubjEMail'),
                    pszSubjDNS=sign_info.get('pszSubjDNS'),
                    pszSubjEDRPOUCode=sign_info.get('pszSubjEDRPOUCode'),
                    pszSubjDRFOCode=sign_info.get('pszSubjDRFOCode'),
                    pszSubjLocality=sign_info.get('pszSubjLocality'),
                )
                cert.save()
    else:
        try:
            cert = CertificateOwner.objects.get(pszSerial=post_data['serial'])
        except CertificateOwner.DoesNotExist:
            # Запись данных ключа в БД
            cert = CertificateOwner(
                pszIssuer=post_data['issuer'],
                pszIssuerCN=post_data['issuerCN'],
                pszSerial=post_data['serial'],
                pszSubject=post_data['subject'],
                pszSubjCN=post_data['subjCN'],
                pszSubjOrg=post_data['subjOrg'],
                pszSubjOrgUnit=post_data['subjOrgUnit'],
                pszSubjTitle=post_data['subjTitle'],
                pszSubjState=post_data['subjState'],
                pszSubjFullName=post_data['subjFullName'],
                pszSubjAddress=post_data['subjAddress'],
                pszSubjPhone=post_data['subjPhone'],
                pszSubjEMail=post_data['subjEMail'],
                pszSubjDNS=post_data['subjDNS'],
                pszSubjEDRPOUCode=post_data['subjEDRPOUCode'],
                pszSubjDRFOCode=post_data['subjDRFOCode'],
                pszSubjLocality=post_data['subjLocality'],
            )
            cert.save()

    return cert


def certificate_get_user_names(cert_id: int) -> list:
    """Возвращает список имён пользователя из сертификата (pszSubjFullName, pszSubjCN)."""
    cert = CertificateOwner.objects.filter(pk=cert_id).first()
    if cert:
        return [cert.pszSubjFullName, cert.pszSubjCN]
    return []


def certificate_get_data(cert_id: int):
    """Возвращает данные сертификата"""
    cert = CertificateOwner.objects.filter(pk=cert_id).defer('id', 'user_id').values().first()
    return cert


def user_get_or_create_from_cert(cert_data: dict):
    """Создаёт и/или возвращает пользователя из данных сертификата ЭЦП."""
    cert, created = CertificateOwner.objects.get_or_create(
        pszSerial=cert_data['pszSerial'],
        defaults={
            'pszIssuer': cert_data['pszIssuer'],
            'pszIssuerCN': cert_data['pszIssuerCN'],
            'pszSubject': cert_data['pszSubject'],
            'pszSubjCN': cert_data['pszSubjCN'],
            'pszSubjOrg': cert_data['pszSubjOrg'],
            'pszSubjOrgUnit': cert_data['pszSubjOrgUnit'],
            'pszSubjTitle': cert_data['pszSubjTitle'],
            'pszSubjState': cert_data['pszSubjState'],
            'pszSubjFullName': cert_data['pszSubjFullName'],
            'pszSubjAddress': cert_data['pszSubjAddress'],
            'pszSubjPhone': cert_data['pszSubjPhone'],
            'pszSubjEMail': cert_data['pszSubjEMail'],
            'pszSubjDNS': cert_data['pszSubjDNS'],
            'pszSubjEDRPOUCode': cert_data['pszSubjEDRPOUCode'],
            'pszSubjDRFOCode': cert_data['pszSubjDRFOCode'],
            'pszSubjLocality': cert_data['pszSubjLocality'],
        }
    )
    return cert.user


def user_get_appeals_user_list_qs() -> Iterable[UserModel]:
    """Возвращает Queryset членов апеляционной палаты."""
    users = User.objects.filter(
        groups__name='Член Апеляційної палати',
    ).annotate(
        cases_finished_num=Count('collegiummembership', filter=Q(collegiummembership__case__stopped=True)),
        cases_current_num=Count('collegiummembership', filter=Q(collegiummembership__case__stopped=False)),
    ).prefetch_related(
        Prefetch('specialities', queryset=ObjKind.objects.order_by('title')),
        'collegium',
        'absence_set',
    ).order_by(
        'last_name', 'first_name', 'middle_name'
    )

    return users
