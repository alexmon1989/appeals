/* eslint-disable */
import * as IEUSignCP from '@/app/lib/ds/js/eusw.umd'
import { randomString } from '@/app/lib/until'

let euSign = null

const EU_SIGN_WEB_EXTENSION_ADDRESS_CHROME = 'chrome-extension://jffafkigfgmjafhpkoibhfefeaebmccg/'
const EU_SIGN_WEB_EXTENSION_ADDRESS_FIREFOX = 'eusw@iit.com.ua'
const EU_SIGN_WEB_EXTENSION_ADDRESS = EU_SIGN_WEB_EXTENSION_ADDRESS_CHROME

function getBrowserId () {
  const aKeys = ['Chrome', 'Firefox', 'Opera', 'Safari']
  const sUsrAg = navigator.userAgent
  let nIdx = aKeys.length - 1
  for (nIdx; nIdx > -1 && sUsrAg.indexOf(aKeys[nIdx]) === -1; nIdx--) {

  }
  return nIdx
}

export function EUSInit () {
  const EUSignCP = IEUSignCP.EUSignCP
  const EndUserLibraryLoader = IEUSignCP.EndUserLibraryLoader
  let types
  let devices = []

  async function _getFlatArray (methodName, from = 0, to = 128, ...args) {
    const self = this
    const result = []

    let range = {
      [Symbol.asyncIterator] () {
        return {
          current: from,
          last: to,
          async next () {
            const value = await new Promise((resolve, reject) => self[methodName](
              ...args,
              this.current,
              resolve,
              reject
            ))
            if (this.current <= this.last && value !== '') {
              this.current++
              return {
                done: false,
                value: value
              }
            } else {
              return { done: true }
            }
          }
        }
      }
    }

    for await (let value of range) {
      result.push(value)
    }
    return result
  }

  async function _eusLoader () {
    return new Promise((resolve, reject) => {
      const libType = EndUserLibraryLoader.LIBRARY_TYPE_DEFAULT
      const objId = 'euSignDom'
      const langCode = EndUserLibraryLoader.EU_DEFAULT_LANG
      const loader = new EndUserLibraryLoader(libType, objId, langCode)

      loader.onload = function (library) {
        console.log('Library loaded')

        euSign = library
        euSign.Initialize(
          function () {
            console.log('Library initialized')
            resolve(euSign)
          },
          function (e) {
            reject(e)
          })
      }

      loader.onerror = function (e) {
        reject(e)
      }

      loader.load()
    })
  }

  return new Promise(async (resolve, reject) => {
    try {
      const euSign = await _eusLoader()
      euSign.__proto__.GetKeyInfoBinaryAsync = function (privateKey, password) {
        return new Promise((resolve, reject) => {
          euSign.GetKeyInfoBinary(privateKey, password, resolve, reject)
        })
      }

      euSign.__proto__.GetKeyInfoSilentlyAsync = function (typeIndex, devIndex, password) {
        return new Promise((resolve, reject) => {
          euSign.GetKeyInfoSilently(typeIndex, devIndex, password, resolve, reject)
        })
      }

      euSign.__proto__.GetCertificatesByKeyInfoAsync = function (keyInfo, cmpServers, cmpPorts) {
        return new Promise((resolve, reject) => {
          euSign.GetCertificatesByKeyInfo(keyInfo, cmpServers, cmpPorts, resolve, reject)
        })
      }

      euSign.__proto__.ReadPrivateKeyBinaryAsync = function (privateKey, password) {
        return new Promise((resolve, reject) => {
          euSign.ReadPrivateKeyBinary(privateKey, password, resolve, reject)
        })
      }

      euSign.__proto__.ReadPrivateKeySilentlyAsync = function (typeIndex, devIndex, password) {
        return new Promise((resolve, reject) => {
          euSign.ReadPrivateKeySilently(typeIndex, devIndex, password, resolve, reject)
        })
      }

      euSign.__proto__.GetPrivateKeyOwnerInfoAsync = function () {
        return new Promise((resolve, reject) => {
          euSign.GetPrivateKeyOwnerInfo(resolve, reject)
        })
      }

      euSign.__proto__.AsyncGetKeyMediaTypes = async function () {
        types = await _getFlatArray.call(euSign, 'EnumKeyMediaTypes')
        const excludeTypes = [0, 1, 2, 13, 14, 15, 40];
        return types
          .map((type, index) => ({
            title: type,
            index
          }))
          .filter(type => !excludeTypes.some(item => item === type.index))
      }

      euSign.__proto__.AsyncGetKeyMediaDevices = async function (index) {
        return await _getFlatArray.call(euSign, 'EnumKeyMediaDevices', 0, 4, index)
      }

      euSign.__proto__.getAllKeys = async function (types) {
        for await (const type of types) {
          console.log('type: ', type)
          let keyDevices = await euSign.AsyncGetKeyMediaDevices(type.index)
          if (keyDevices.length) {
            devices.push(...keyDevices
              .map((device, i) => ({
                typeIndex: type.index,
                device,
                devIndex: i,
                uniqueId: randomString()
              })))
          }
        }
        return devices
      }

      euSign.__proto__.BytesToStringAsync = async function (data) {
        return new Promise((resolve, reject) => {
          euSign.BytesToString(data, resolve, reject)
        })
      }

      euSign.__proto__.BASE64EncodeAsync = async function (data) {
        return new Promise((resolve, reject) => {
          euSign.BASE64Encode(data, resolve, reject)
        })
      }

      euSign.__proto__.GetOwnCertificatesAsync = async function (index) {
        return new Promise((resolve, reject) => {
          euSign.EnumOwnCertificates(index, resolve, reject)
        })
      }

      euSign.__proto__.SignAsync = async function (data) {
        return new Promise((resolve, reject) => {
          euSign.Sign(true, data, resolve, reject)
        })
      }

      euSign.__proto__.SaveCertificatesAsync = async function (cert) {
        return new Promise((resolve, reject) => {
          euSign.SaveCertificates(cert, resolve, reject)
        })
      }

      euSign.__proto__.VerifyAsync = async function (signature, data) {
        const showSignerInfo = {}
        return new Promise((resolve, reject) => {
           euSign.Verify(signature, data, showSignerInfo, resolve, reject)
        })
      }

      resolve(euSign)
    } catch (e) {
      reject(e)
    }
  })
}
