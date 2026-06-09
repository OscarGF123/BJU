// Manejo de error de permisos y cuentas inactivas

window.handlePermissionError = function(data, defaultRedirect = '/login'){
    Swal.fire({
        title: 'Error',
        icon: 'error',
        text: data.message,
        confirmButtonText: 'Entendido'
    })
    .then(() =>{
        window.location.href = data.redirect_url || defaultRedirect;
    });
}

// ========================================
// FUNCIONES DE UTILIDAD
// ========================================

// Formatear precios en pesos colombianos
window.formatPrice = function(price) {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0
    }).format(price);
}

// Validar email (para futuros formularios)
window.validateEmail = function (email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Función para cambiar tema (light/dark) - funcionalidad futura
window.toggleTheme = function () {
    document.body.classList.toggle('light-theme');
    // Guardar preferencia en localStorage sería ideal aquí
    // pero recordemos que localStorage no está disponible en artifacts
}


const csrftoken = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1];

// Para actualizar la cantidad de un producto en el carrito de compras
window.actualizarCantidad = function (item_id, cantidad){
    const formData = new FormData();
    formData.append('cantidad', cantidad);

    return fetch(`/carrito/actualizar_cantidad_producto/${item_id}`,{
        'method': 'POST',
        'headers': {
            'X-CSRFToken': csrftoken
        },
        'body': formData
    })
    .then(r => r.json())
}

window.seleccionarItem = function (producto_id=null, seleccionado=null, seleccionarTodo=null){
    const formData = new FormData();
    if (seleccionarTodo!==null){
        formData.append('seleccionar_todo', seleccionarTodo)
    } else if (producto_id!==null && seleccionado!==null) {
        formData.append('seleccionado', seleccionado);
        formData.append('producto_id', producto_id)
    }
    return fetch('/carrito/seleccionar_item/', {
        'method': 'POST',
        'headers': {
            'X-CSRFToken': csrftoken
        },
        'body': formData
    }).then(r => r.json())

}