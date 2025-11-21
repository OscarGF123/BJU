const scriptRegistro = document.getElementById("registroScript");
let urlRegistro = scriptRegistro.dataset.urlregistro;

//csrf_token

function getCookie(name) {
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

const csrftoken = getCookie('csrftoken');

document.getElementById("formularioRegistro").addEventListener('submit', function(e){
    e.preventDefault();

    fetch(urlRegistro, {
        method: "POST",
        headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest',
        },
        body: new FormData(this)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success"){

            window.location.href = data.redirect_url;

        } else {

            alert(`Ha ocurrido un error \n${data}`);

        }
    })
    .catch(error => {
        console.log(error);
    });

});