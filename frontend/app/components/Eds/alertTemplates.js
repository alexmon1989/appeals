
export const ownerInfo = (subjCN, issuerCN, serial) => {
  return `
    <div>Власник: ${subjCN}</div>
    <div>ЦСК: ${issuerCN}</div>
    <div>Серійний номер: ${serial}</div>
  `
}

export const errorAlert = (code = 0, message = 'Невідома помилка') => {
  return `
    <div>${message}</div>
    <div>Код помилки: ${code}</div>
  `
}

export const errorAlert4097 = (html) => {
  return `
  <p>Виникла помилка при взаємодії з криптографічною бібліотекою. Бібліотеку web-підпису не запущено
  або не інстальовано у системі. Для продовження необхідно запустити або інсталювати бібліотеку web-підпису.</p>
  <p>
  <div><a target="_blank" href="https://iit.com.ua/download/productfiles/EUSignWebInstall.exe ">Інсталяційний пакет web-бібліотеки підпису</a></div>
  <div><a target="_blank" href="https://acskidd.gov.ua/download/manual/EU13OManualDPS.pdf">Настанови користувача</a></div>
</p>
  `
}
