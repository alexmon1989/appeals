/* eslint-disable */
importScripts(
  '/static/ds/js/euverifysign.types.js',
  '/static/ds/js/euscpt.js',
  '/static/ds/js/euscpm.js',
  '/static/ds/js/euscp.js');

/* eslint-disable */
//==============================================================================

function EUSignInit() {
  var URL_CAS_CERTIFICATES = "/static/ds/eus/CACertificates.p7b";
  var URL_CAS = "/static/ds/eus/CAs.json";
  var URL_XML_HTTP_PROXY_SERVICE = "/proxy_handler/ProxyHandlerCURL.php";

  var CZO_SERVER = "czo.gov.ua"

//==============================================================================

  var s_loaded = false;
  var s_verifyLargeFiles = true;
  var s_cas = null;

//==============================================================================

  function sendMessage(data, e, params) {
    var error = (e != null) ?
      {'errorCode': e.errorCode, 'message': e.message} : null;
  }

//==============================================================================

  function LoadCAsCertificates(onSuccess, onError) {
    var _onSuccess = function(certificates) {
      try {
        euSign.SaveCertificates(certificates);
        onSuccess();
      } catch (e) {
        onError(e);
      }
    };

    euSign.LoadDataFromServer(URL_CAS_CERTIFICATES,
      _onSuccess, onError, true);
  };

//------------------------------------------------------------------------------
  function SetXMLHTTPDirectAccess() {
    var _addDNSName = function(uri, dnsNames) {
      if (uri == '')
        return;

      uri = (uri.indexOf("://") > -1) ?
        uri.split('/')[2] :
        uri.split('/')[0];

      if (dnsNames.indexOf(uri) >= 0)
        return;

      dnsNames.push(uri);
    };

    var CAsWithDirectAccess = [];
    euSign.SetXMLHTTPDirectAccess(true);
    CAsWithDirectAccess.push(CZO_SERVER);
    for (var i = 0; i < s_cas.length; i++) {
      if (!s_cas[i].directAccess)
        continue;

      _addDNSName(s_cas[i].address, CAsWithDirectAccess);
      _addDNSName(s_cas[i].tspAddress, CAsWithDirectAccess);
     // _addDNSName(s_cas[i].cmpAddress, CAsWithDirectAccess);
      _addDNSName(s_cas[i].ocspAccessPointAddress,
        CAsWithDirectAccess);
    }

    CAsWithDirectAccess.forEach(function(address) {
      euSign.AddXMLHTTPDirectAccessAddress(address);
    });
  };

  function LoadCAs(onSuccess, onError) {
    var _onSuccess = function(response) {
      try {
        var cas = JSON.parse(response.replace(/\\'/g, "'"));

        s_cas = cas;
        euSign.CAs = cas;
        onSuccess(cas);
      } catch (e) {
        // errorHandler ? errorHandler() : null
        console.log(e)
        onError(e);
      }
    };

    euSign.LoadDataFromServer(URL_CAS, _onSuccess, onError, false);
  };

//------------------------------------------------------------------------------

  function SetOCSPAccessInfoSettings() {
    var settings = euSign.CreateOCSPAccessInfoModeSettings();
    settings.SetEnabled(true);
    euSign.SetOCSPAccessInfoModeSettings(settings);

    settings = euSign.CreateOCSPAccessInfoSettings();
    for (var i = 0; i < s_cas.length; i++) {
      settings.SetAddress(s_cas[i].ocspAccessPointAddress);
      settings.SetPort(s_cas[i].ocspAccessPointPort);

      for (var j = 0; j < s_cas[i].issuerCNs.length; j++) {
        settings.SetIssuerCN(s_cas[i].issuerCNs[j]);
        euSign.SetOCSPAccessInfoSettings(settings);
      }
    }
    console.log('settings: ', settings)
  };

  function SetSettings(onSuccess, onError) {
    try {
      euSign.SetXMLHTTPProxyService(URL_XML_HTTP_PROXY_SERVICE);

      var settings = euSign.CreateFileStoreSettings();
      settings.SetPath('');
      settings.SetSaveLoadedCerts(true);
      euSign.SetFileStoreSettings(settings);

      settings = euSign.CreateProxySettings();
      euSign.SetProxySettings(settings);

      settings = euSign.CreateTSPSettings();
      settings.SetGetStamps(true)
      euSign.SetTSPSettings(settings);

      settings = euSign.CreateOCSPSettings();
      settings.SetUseOCSP(true);
      settings.SetBeforeStore(true);
      settings.SetAddress('');
      settings.SetPort('80');
      euSign.SetOCSPSettings(settings);

      // settings = euSign.CreateCMPSettings();
      // euSign.SetCMPSettings(settings);

      settings = euSign.CreateLDAPSettings();
      euSign.SetLDAPSettings(settings);

      LoadCAs(
        function() {
          try {
            console.log('direct')
            SetOCSPAccessInfoSettings();
            SetXMLHTTPDirectAccess();
            onSuccess();
          } catch (e) {
            onError(e);
          }
        }, onError);
    } catch (e) {
      onError(e);
    }
  }

//==============================================================================

  function Initialize(data) {
    try {
      s_verifyLargeFiles = data.params.verifyLargeFiles;
      euSign.SetErrorMessageLanguage(data.params.langCode);
      euSign.Initialize();

      var _onSuccess = function() {
        var params = {
          'isFileSyncAPISupported' : euSign.isFileSyncAPISupported,
          'isFileASyncAPISupported': euSign.isFileASyncAPISupported
        };

        sendMessage(data, null, params);
      }

      var _onError = function(e) {
        sendMessage(data, e, null);
      };

      if (euSign.DoesNeedSetSettings()) {
        var _onSuccessSetSettings = function() {
          LoadCAsCertificates(_onSuccess, _onError);
        };

        SetSettings(_onSuccessSetSettings, _onError);
      } else {
        LoadCAsCertificates(_onSuccess, _onError);
      }
    } catch (e) {
      sendMessage(data, e, null);
      return;
    }
  }

  var euSign = EUSignCP();
  Initialize({
    callback_id: 1,
    cmd: "Initialize",
    params: {langCode: 0, verifyLargeFiles: true}
  });
  return euSign;

//==============================================================================
}

let euSign;

var EUSignCPModuleInitialized = function (isInit) {
  euSign = EUSignInit();
  postMessage({
    event: 'EUSIGN_INIT',
    interface: Object.keys(euSign.__proto__)
  });
}

onmessage = function(e) {
  const { methodName, args, requestKey } = e.data;
  console.log('Worker: ', methodName, args, requestKey);
  try {
    const res = euSign[methodName](...args);
    postMessage({
      event: 'RESULT',
      type: 'RESOLVE',
      requestKey: requestKey,
      result: res
    });
  } catch (err) {
    postMessage({
      event: 'RESULT',
      type: 'REJECT',
      requestKey: requestKey,
      error: {errorCode: err.ErrorCode, message: err.message}
    });
    console.log('ERR: ', err)
  }
}

