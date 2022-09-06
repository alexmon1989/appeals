window.addEventListener("load", function (event) {
    const headDiv = document.querySelector('#div_id_head div')
    const membersDiv = document.querySelector('#div_id_members div')

    headDiv.classList.add('disabled')
    membersDiv.classList.add('disabled')

    const p = document.getElementById('desc')
    p.addEventListener('dblclick', (e) => {
      headDiv.classList.toggle('disabled');
      membersDiv.classList.toggle('disabled');
    });
});
