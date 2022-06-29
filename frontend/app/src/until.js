/* eslint-disable */

export const randomString = () => Math.random().toString(36).substring(8)

export const getOSType = () => {
  let OSName = "Unknown";
  if (window.navigator.userAgent.indexOf("Windows NT")!= -1) return "Windows";
  if (window.navigator.userAgent.indexOf("Mac")            != -1) return "MacOS";
  if (window.navigator.userAgent.indexOf("Linux")          != -1) return "Linux";
}

export const getBrowserName = function () {
  const aKeys = ["Chrome", "Firefox", "Opera"];
  const sUsrAg = navigator.userAgent;
  let nIdx = aKeys.length - 1;
  for (nIdx; nIdx > -1 && sUsrAg.indexOf(aKeys[nIdx]) === -1; nIdx--);
  return aKeys[nIdx]
}

export const reqFactory = data => {
  return {
    dtoModelName: '',
    version: '0.1.0',
    data: {
      dtoModelName: '',
      version: '0.1.0',
      ...data
    }
  }
}

export const getCookie = function (name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

export const getFileUint8Array = async function (url) {
  // Возвращает ArrayBuffer файла
  let response = await fetch(url)
  let CONTENT = await response.blob()

  return new Promise((resolve, reject) => {
    let fr = new FileReader();
    fr.onloadend = () => {
      const result = new Uint8Array(fr.result)
      resolve(result);
    };
    fr.onerror = reject;
    fr.readAsArrayBuffer(CONTENT);
  });
}

export const uploadSign = async function (documentId, signData, signInfo) {
  const csrftoken = getCookie('csrftoken')
  let blob = new Blob([signData], {type: "application/octet-stream"})

  const data = new FormData()
  data.append('blob', blob);
  data.append('sign_info', JSON.stringify(signInfo))

  const request = new Request(
      '/cases/upload-sign/' + documentId + '/',
      {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        mode: 'same-origin',
        body: data
      }
  );

  const response = await fetch(request)
  return await response.json()
}


export const getTaskResult = async function (taskId, maxRetries = 20, currentTry = 1) {
    const url = '/filling/get-task-result/' + taskId

    let response = await fetch(url)
    let json = await response.json()

    if (json.task_status === 'SUCCESS') {
        return json.task_result
    } else if (json.task_status === 'PENDING') {
        if (currentTry === maxRetries) {
            throw new Error("Max retries count reached.")
        }
        currentTry++
        await new Promise(r => setTimeout(r, 2000));
        return await getTaskResult(taskId, maxRetries, currentTry)
    }
}
