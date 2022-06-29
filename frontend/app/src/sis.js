import { getTaskResult } from '@/app/src/until'

const APP_STRUCTURE = {
    'app_date': '',
    'obj_title': '',
    'applicant_title': '',
    'applicant_address': '',
    'represent_title': '',
    'represent_address': '',
    'mailing_address': '',
}

const REG_DOC_STRUCTURE = {
    'app_number': '',
    'app_date': '',
    'obj_title': '',
    'owner_title': '',
    'owner_address': '',
    'represent_title': '',
    'represent_address': '',
    'mailing_address': '',
}

function formatDataTM(data, objState) {
    let res = objState === 1 ? APP_STRUCTURE : REG_DOC_STRUCTURE

    if (res.hasOwnProperty('app_number')) {
        res['app_number'] = data['ApplicationNumber']
    }

    if (res.hasOwnProperty('app_date')) {
        const [year, month, day] = data['ApplicationDate'].split('-')
        res['app_date'] = [day, month, year].join('.')
    }

    if (res.hasOwnProperty('obj_title')) {
        const words = data['WordMarkSpecification']['MarkSignificantVerbalElement']
        let words_res = []
        words.forEach(word => words_res.push(word['#text']));
        res['obj_title'] = words_res.join(', ')
    }

    if (res.hasOwnProperty('applicant_title')) {
        try {
            res['applicant_title'] = data['ApplicantDetails']['Applicant'][0]['ApplicantAddressBook']['FormattedNameAddress']['Name']['FreeFormatName']['FreeFormatNameDetails']['FreeFormatNameLine']
        } catch (e) {
            res['applicant_title'] = ''
        }
    }

    if (res.hasOwnProperty('applicant_address')) {
        try {
            res['applicant_address'] = data['ApplicantDetails']['Applicant'][0]['ApplicantAddressBook']['FormattedNameAddress']['Address']['FreeFormatAddress']['FreeFormatAddressLine']
        } catch (e) {
            res['applicant_address'] = ''
        }
    }

    if (res.hasOwnProperty('owner_title')) {
        try {
            res['owner_title'] = data['ApplicantDetails']['Applicant'][0]['ApplicantAddressBook']['FormattedNameAddress']['Name']['FreeFormatName']['FreeFormatNameDetails']['FreeFormatNameLine']
        } catch (e) {
            res['owner_title'] = ''
        }
    }

    if (res.hasOwnProperty('owner_address')) {
        try {
            res['owner_address'] = data['ApplicantDetails']['Applicant'][0]['ApplicantAddressBook']['FormattedNameAddress']['Address']['FreeFormatAddress']['FreeFormatAddressLine']
        } catch (e) {
            res['owner_address'] = ''
        }
    }

    if (res.hasOwnProperty('represent_title')) {
        try {
            res['represent_title'] = data['RepresentativeDetails']['Representative'][0]['RepresentativeAddressBook']['FormattedNameAddress']['Name']['FreeFormatName']['FreeFormatNameDetails']['FreeFormatNameDetails']['FreeFormatNameLine']
        } catch (e) {
            res['represent_title'] = ''
        }
    }

    if (res.hasOwnProperty('represent_address')) {
        try {
            res['represent_address'] = data['RepresentativeDetails']['Representative'][0]['RepresentativeAddressBook']['FormattedNameAddress']['Address']['FreeFormatAddress']['FreeFormatAddressLine']
        } catch (e) {
            res['represent_address'] = ''
        }
    }

    if (res.hasOwnProperty('mailing_address')) {
        try {
            res['mailing_address'] = data['CorrespondenceAddress']['CorrespondenceAddressBook']['Address']['FreeFormatAddressLine']
            res['mailing_address'] += '\n' + data['CorrespondenceAddress']['CorrespondenceAddressBook']['Name']['FreeFormatNameLine']
        } catch (e) {
            res['mailing_address'] = ''
        }
    }

    return res
}

function formatDataID(data, objState) {
    let res = objState === 1 ? APP_STRUCTURE : REG_DOC_STRUCTURE

    if (res.hasOwnProperty('app_number')) {
        res['app_number'] = data['DesignApplicationNumber']
    }

    if (res.hasOwnProperty('app_date')) {
        const [year, month, day] = data['DesignApplicationDate'].split('-')
        res['app_date'] = [day, month, year].join('.')
    }

    if (res.hasOwnProperty('obj_title')) {
        res['obj_title'] = data['DesignTitle']
    }

    if (res.hasOwnProperty('applicant_title')) {
        try {
            res['applicant_title'] = data['ApplicantDetails']['Applicant'][0]['ApplicantAddressBook']['FormattedNameAddress']['Name']['FreeFormatName']['FreeFormatNameDetails']['FreeFormatNameLine']
        } catch (e) {
            res['applicant_title'] = ''
        }
    }

    if (res.hasOwnProperty('applicant_address')) {
        try {
            res['applicant_address'] = data['ApplicantDetails']['Applicant'][0]['ApplicantAddressBook']['FormattedNameAddress']['Address']['FreeFormatAddress']['FreeFormatAddressLine']
        } catch (e) {
            res['applicant_address'] = ''
        }
    }

    if (res.hasOwnProperty('owner_title')) {
        try {
            res['owner_title'] = data['ApplicantDetails']['Applicant'][0]['ApplicantAddressBook']['FormattedNameAddress']['Name']['FreeFormatName']['FreeFormatNameDetails']['FreeFormatNameLine']
        } catch (e) {
            res['owner_title'] = ''
        }
    }

    if (res.hasOwnProperty('owner_address')) {
        try {
            res['owner_address'] = data['ApplicantDetails']['Applicant'][0]['ApplicantAddressBook']['FormattedNameAddress']['Address']['FreeFormatAddress']['FreeFormatAddressLine']
        } catch (e) {
            res['owner_address'] = ''
        }
    }

    if (res.hasOwnProperty('represent_title')) {
        try {
            res['represent_title'] = data['RepresentativeDetails']['Representative'][0]['RepresentativeAddressBook']['FormattedNameAddress']['Name']['FreeFormatName']['FreeFormatNameDetails']['FreeFormatNameLine']
        } catch (e) {
            res['represent_title'] = ''
        }
    }

    if (res.hasOwnProperty('represent_address')) {
        try {
            res['represent_address'] = data['RepresentativeDetails']['Representative'][0]['RepresentativeAddressBook']['FormattedNameAddress']['Address']['FreeFormatAddress']['FreeFormatAddressLine']
        } catch (e) {
            res['represent_address'] = ''
        }
    }

    if (res.hasOwnProperty('mailing_address')) {
        try {
            res['mailing_address'] = data['CorrespondenceAddress']['CorrespondenceAddressBook']['Address']['FreeFormatAddressLine']
            res['mailing_address'] += '\n' + data['CorrespondenceAddress']['CorrespondenceAddressBook']['Name']['FreeFormatNameLine']
        } catch (e) {
            res['mailing_address'] = ''
        }
    }

    return res
}

function formatDataInvUmLd(data, objState) {
    let res = objState === 1 ? APP_STRUCTURE : REG_DOC_STRUCTURE

    if (res.hasOwnProperty('app_number')) {
        res['app_number'] = data['I_21']
    }

    if (res.hasOwnProperty('app_date')) {
        const [year, month, day] = data['I_22'].split('-')
        res['app_date'] = [day, month, year].join('.')
    }

    if (res.hasOwnProperty('obj_title')) {
        res['obj_title'] = Object.values(data['I_54'][0])[0]
    }

    if (res.hasOwnProperty('applicant_title')) {
        let applicants = []
        try {
            let values = Object.values(data['I_71'])
            for (let i = 0; i < values.length; i++) {
                applicants.push(Object.values(values[i]).sort(
                    (x, y) => y.length - x.length
                )[0])
            }
        } catch (e) {
            res['applicant_title'] = ''
        }
        res['applicant_title'] = applicants.join('\n')
    }

    if (res.hasOwnProperty('owner_title')) {
        let owners = []
        try {
            let values = Object.values(data['I_71'])
            for (let i = 0; i < values.length; i++) {
                owners.push(Object.values(values[i]).sort(
                    (x, y) => y.length - x.length
                )[0])
            }
        } catch (e) {
            res['owner_title'] = ''
        }
        res['owner_title'] = owners.join('\n')
    }

    if (res.hasOwnProperty('represent_title')) {
        try {
            res['represent_title'] = data['I_74']
        } catch (e) {
            res['represent_title'] = ''
        }
    }

    if (res.hasOwnProperty('mailing_address')) {
        try {
            res['mailing_address'] = data['I_98']
        } catch (e) {
            res['mailing_address'] = ''
        }
    }

    return res
}

// Получает данные заявки/охранного документа из СИС и возвращает их в отформатированном виде
async function getDataFromSIS(numType, num, objKindIdSIS) {
    let objState = numType === 'app_number' ? 1 : 2
    // let url = 'https://sis.ukrpatent.org/api/v1/open-data/search/?strict_search=true'
    let url = '/filling/get-data-from-sis/'
    url += '?obj_num_type=' + numType
    url += '&obj_number=' + num
    url += '&obj_kind_id_sis=' + objKindIdSIS
    url += '&obj_state=' + objState

    let response = await fetch(url)
    let res = {}

    if (response.ok) {
        let json = await response.json()
        const taskId = json.task_id

        const taskResult = await getTaskResult(taskId)

        // Проверка есть ли библ. данные по объекту
        if (Object.keys(taskResult).length === 0) {
            return res
        }

        const data = taskResult.data
        switch(objKindIdSIS) {
          case 1:
              res = formatDataInvUmLd(data, objState);
              break
          case 2:
              res = formatDataInvUmLd(data, objState);
              break
          case 3:
              res = formatDataInvUmLd(data, objState);
              break
          case 4:
              res = formatDataTM(data, objState);
              break
          case 6:
              res = formatDataID(data, objState);
              break
          default:
              throw new Error("Unknown object type")
        }

        return res

    } else {
        throw new Error("HTTP Error: " + response.status)
    }
}

export { getDataFromSIS as default }