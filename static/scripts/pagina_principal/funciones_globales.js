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
    if (!price){
        return 0
    }
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


window.actualizarTotal = function (subtotal, descuento, total) {
    let dTotal = document.querySelector('#miniCartTotal');
    let dDescuento = document.querySelector('#miniCartDescuento');
    let dSubtotal = document.querySelector('#miniCartSubtotal');

    dTotal.textContent = window.formatPrice(total);
    dDescuento.textContent = `-${window.formatPrice(descuento)}`;
    dSubtotal.textContent = window.formatPrice(subtotal);
}

const csrftoken = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1];

// Para actualizar la cantidad de un producto en el carrito de compras
window.actualizarCantidad = function (item_id, cantidad){
    const formData = new FormData();
    formData.append('cantidad', cantidad===''?1:cantidad);

    return fetch(`/carrito/actualizar_cantidad_producto/${item_id}`,{
        'method': 'POST',
        'headers': {
            'X-CSRFToken': csrftoken
        },
        'body': formData
    })
    .then(r => r.json())
}

window.seleccionarItem = function (item_id=null, seleccionado=null, seleccionarTodo=null){
    const formData = new FormData();
    if (seleccionarTodo!==null){
        formData.append('seleccionar_todo', seleccionarTodo)
    } else if (item_id!==null && seleccionado!==null) {
        formData.append('seleccionado', seleccionado);
        formData.append('item_id', item_id)
    }
    return fetch('/carrito/seleccionar_item/', {
        'method': 'POST',
        'headers': {
            'X-CSRFToken': csrftoken
        },
        'body': formData
    }).then(r => r.json())

}