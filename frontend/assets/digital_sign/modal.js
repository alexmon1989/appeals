let dsModal = document.getElementById('ds-modal')

dsModal.addEventListener('show.bs.modal', function (event) {
    let button = event.relatedTarget
    let docName = button.getAttribute('data-bs-document-name')
    let docUrl = button.getAttribute('data-bs-document-url')
    let docId = button.getAttribute('data-bs-document-id')

    let signButton = dsModal.querySelector('#sign-file-btn')
    let aFileUrl = dsModal.querySelector('#file-url')
    let aFileName = dsModal.querySelector('#file-name')

    signButton.onclick = function () {
        euSignTest.processFile(docId, docUrl)
    };

    aFileName.textContent = docName
    aFileUrl.href = docUrl
})
