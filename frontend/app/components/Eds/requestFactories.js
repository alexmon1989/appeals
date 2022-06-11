import config from '../../config'

export const reqSignInEDSFactory = (keyInfo) => {
  return {
    dtoModelName: 'SignInRequest',
    version: '0.1.0',
    headers: {
      service: {
        name: config.serviceName,
        version: config.serviceVersion
      }
    },
    data: {
      dtoModelName: 'UserDtoModelSignInEdsRequest',
      version: '0.1.0',
      issuer: keyInfo.issuer,
      issuerCN: keyInfo.issuerCN,
      serial: keyInfo.serial,
      subjCN: keyInfo.subjCN,
      subjDRFOCode: keyInfo.subjDRFOCode,
      subjEDRPOUCode: keyInfo.subjEDRPOUCode,
      subjEMail: keyInfo.subjEMail,
      subjPhone: keyInfo.subjPhone,
      subjFullName: keyInfo.subjFullName,
      subjLocality: keyInfo.subjLocality,
      subjOrg: keyInfo.subjOrg,
      subjOrgUnit: keyInfo.subjOrgUnit,
      subjTitle: keyInfo.subjTitle,
      keyInfoArr: keyInfo.keyInfoArr
    }
  }
}
