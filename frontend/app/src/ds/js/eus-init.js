/* eslint-disable */
const random = () => (Math.random() + 1).toString(36).substring(7);

export const EUSWorkerInit = function () {
  const requests = [];
  return new Promise((resolve, reject) => {
    const intFace = {};
    const eusWorker = new Worker('/static/ds/js/eusign.worker.js');
    const eusHandler = (methodName, ...args) => {
      return new Promise((resolve, reject) => {
        const requestKey = random();
        requests.push({
          requestKey,
          resolve,
          reject
        })
        eusWorker.postMessage({
          methodName,
          args,
          requestKey: requestKey
        });
      })
    }
    eusWorker.onmessage = function(e) {
      const event = e.data.event;
      if (event === 'EUSIGN_INIT') {
        e.data.interface.forEach(methodName => {
          intFace[methodName] = eusHandler.bind(null, methodName)
        })
        intFace.SignAsync = (data) => {
          return new Promise(async (resolve, reject) => {
            try {
              const res = await intFace.SignData(data, false);
              resolve(res);
            } catch (err) {
              reject(err);
            }
          })
        }
        intFace.VerifyAsync = eusHandler.bind(null, 'VerifyData')
        resolve(intFace);
      }
      if (event === 'RESULT') {
        const request = requests.find(req => req.requestKey === e.data.requestKey);
        e.data.type === 'RESOLVE' ? request.resolve(e.data.result) : request.reject(e.data.error)
      }
      // Видалення запиту з масиву запитів
      const index = requests.findIndex(req => req.requestKey === e.data.requestKey);
      requests.splice(index, 1);
    }
  })
}
