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

// urls
let script = document.querySelector("#scriptTabla");

let url_editar = script.dataset.editar;
let url_eliminar = script.dataset.eliminar;

// Nombre del modulo
let seccion = script.dataset.seccion;

// Nombre del modulo con formset
let seccionFormset = "Producto";

// modal formulario
const formulario = document.getElementById("formulario");

// datatable
let tableInstance;

// variable para verificar si se esta haciendo una edicion o no
let modoEdicion = false;
let id_edicion;
let fila_edicion;

// formulario completamente vacio para resetear el formulario
let formularioLimpio;

// variable para guardar el formulario original con valores en los campos
let formularioOriginal;


// ========================================
// FUNCION PARA CERRAR MODAL CORRECTAMENTE
// ========================================
function cerrarModalCorrectamente(modalId) {
    // Quitar foco del elemento activo ANTES de cerrar
    const elementoConFoco = document.querySelector(`#${modalId} :focus`);
    if (elementoConFoco) {
        elementoConFoco.blur();
    }
    
    // Obtener instancia del modal
    const modalElement = document.getElementById(modalId);
    const modal = bootstrap.Modal.getInstance(modalElement);
    
    if (modal) {
        // Cerrar el modal
        modal.hide();
        
        // Mover el foco al body o a un elemento específico
        setTimeout(() => {
            document.body.focus();
            // O si prefieres enfocar la tabla:
            // document.getElementById('datatable')?.focus();
        }, 150);
    }
}

// ========================================
// INICIALIZACIÓN
// ========================================
$(document).ready(function() {
    // Esperar un poco más para asegurar que DataTable esté completamente inicializado
    setTimeout(function() {
        if ($.fn.DataTable.isDataTable('#datatable')) {
            tableInstance = $('#datatable').dataTable().api();
        }
    }, 100);

    // Guardamos el formulario completamente vacio
    formularioLimpio = formulario.innerHTML;

    // Fix global para prevenir el error de aria-hidden
    const modalElement = document.getElementById('formModal');
    if (modalElement) {
        // Cuando el modal se está ocultando
        modalElement.addEventListener('hide.bs.modal', function() {
            // Quitar foco de cualquier elemento dentro del modal
            const focusedElement = this.querySelector(':focus');
            if (focusedElement) {
                focusedElement.blur();
            }
        });

        // Cuando el modal se ha ocultado completamente
        modalElement.addEventListener('hidden.bs.modal', function() {
            // Resetear el formulario
            formulario.innerHTML = formularioLimpio;
            
            // Resetear estado de edición
            modoEdicion = false;
            id_edicion = null;
            fila_edicion = null;
            
            // Resetear título y botón
            document.getElementById("formModalLabel").innerHTML = `
                <i class="fas fa-plus"></i>
                Agregar ${seccion}
            `;
            $("#btnGuardarForm").text(`Guardar ${seccion}`);
            
            // Enfocar el botón que abre el modal (si existe)
            const botonAbrir = document.querySelector('[data-bs-target="#formModal"]');
            if (botonAbrir && !botonAbrir.closest('tr')) {
                botonAbrir.focus();
            }
        });
    }
});

// ========================================
// SUBMIT DEL FORMULARIO
// ========================================
formulario.addEventListener('submit', (e) => {
    e.preventDefault();
    
    // Deshabilitar el botón de guardar para prevenir doble envío
    const btnGuardar = document.getElementById('btnGuardarForm');
    let url_crear = btnGuardar.value;
    // Si se esta agregando un nuevo registro de un formulario adicional tendra una logica diferente
    // evitando que se agregue automaticamente una fila con el registro nuevo
    let agregarFila = btnGuardar.getAttribute("agregarfila") === "false" ? false : true;

    btnGuardar.disabled = true;
    
    // Verifica si se esta editando o se esta agregando
    if (modoEdicion && agregarFila) { // verifica si se esta editando y tambien se esta usando un formulario adicional
        editar();
    } else if (modoEdicion && !agregarFila){
        agregar(url_crear, agregarFila);
    } else {
        agregar(url_crear, agregarFila);
    }
});

// ========================================
// FUNCION AGREGAR
// ========================================
function agregar(url, agregarFila) {
    fetch(url, {
        headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest',
        },
        method: "POST",
        body: new FormData(formulario)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        if (data.status === "success" && agregarFila) {
            let fila = [];
            
            let re = /(?:\.([^.]+))?$/;

            let extensionesValidas = ['jpg', 'png']
            // Tomamos todos los datos registrados Éxitosamente
            for (const clave in data) {
                if (clave !== "status") {
                    if (extensionesValidas.some(extension => extension === re.exec(data[clave])[1])){
                        console.log('Hola');
                        fila.unshift(`
                                <td>
                                    <span data-bs-toggle="modal" data-bs-target="#infoModal" onclick="mostrarImagen('/media/${data[clave]}')">
                                        <a href="#">${data[clave]}</a>
                                    </span>
                                </td>
                            `);
                    } else {
                        fila.unshift(data[clave]);
                    }
                }
            }

            // Agregar botones de acción
            fila.unshift(`
                <button class='bj-btn bj-btn-info bj-btn-sm' id="btn-editar" data-bs-toggle="modal" data-bs-target="#formModal" title="Editar">
                    <i class="fas fa-edit"></i>
                </button>
                <button class='bj-btn bj-btn-danger bj-btn-sm' id="btn-eliminar" data-value="${data.id}"  title="Eliminar">
                    <i class="fas fa-trash"></i>
                </button>
            `);

            // Organizamos los elementos
            fila.reverse();

            // Agregar fila a la tabla
            let nuevaFila = tableInstance.row.add(fila).draw(true);
            $(nuevaFila.node()).attr('id', data.id);
            // Cerrar modal correctamente
            cerrarModalCorrectamente('formModal');
            
            // Alerta
            Swal.fire({
                title: `Éxito!`,
                text: `${seccion} Agregad@ Éxitosamente`,
                icon: 'success'
            });
        } else if (data.status==="success" && !agregarFila){ 

            // en este else if lo que hace es agregar un nuevo registro sin agregarlo a la tabla

            // Obtener el nombre del modelo
            modelo = document.querySelector("#btnGuardarForm").dataset.modelo
            console.log(modelo);

            // regresar al formulario original
            formulario.innerHTML = formularioOriginal;

            const select = document.querySelector(`#id_${modelo}`);
            let opciones = [];

            // tomamos toda la informacion registrada que se obtuvo
            for (const llave in data){
                // excluir el estado de la respuesta
                if (llave !== "status" && llave !== "estado"){
                    opciones.unshift(data[llave]);
                }
            }
            opciones.reverse();
            console.log(opciones)
            //                     nombre        id
            let [texto, valor] = [opciones[1], opciones[0]];
            
            const nuevaOpcion = new Option(texto, valor);

            console.log(nuevaOpcion)
            select.add(nuevaOpcion);
            select.value = valor;

            actualizarSelectFormularioLimpio(modelo, texto, valor);

            // Cambiar el titulo segun si se estaba editando un registro o se estaba creando uno nuevo
            document.getElementById("formModalLabel").innerHTML = modoEdicion
            ?`
            <i class="fas fa-edit"></i>
            Editar ${seccion}
            `
            :`
            <i class="fas fa-plus"></i>
            Agregar ${seccion}
            `
            Swal.fire({
                title: `Éxito!`,
                text: `${seccion} Agregad@ Éxitosamente`,
                icon: 'success'
            });
        } else if(data.status == 'error' && data.type == 'form_invalid'){ // Error en el formulario
            document.getElementById('btnGuardarForm').disabled = false
            // Construir el html con los errores
            let errorMessage = '<ul>';
            for (const [field, messages] of Object.entries(data.errors)) {
                errorMessage += `<li><strong>Campo ${field}:</strong> ${messages.join(', ')}</li>`;
            }
            errorMessage += '</ul>';
            Swal.fire({
                title: 'Error',
                html: `Error en los siguientes campos:<br>${errorMessage}`,
                icon: 'error'
            })
for (let [clave, valor] of new FormData(formulario)) {
    console.log(clave, valor)
}
        } else {
            // evitar errores con el aria-hidden

            let focusedElement = document.querySelector(':focus');
            if (focusedElement) {
                focusedElement.blur();
            }
            handlePermissionError(data);
        }
    });
    // .catch(error => {
    //     console.error('Error:', error);
    //     document.getElementById('btnGuardarForm').disabled = false;

    //     Swal.fire({
    //         title: 'Error',
    //         text: `Ha ocurrido un error inesperado ${error}`,
    //         icon: 'error'
    //     })
    // });

}

// ========================================
// FUNCION EDITAR
// ========================================
function editar() {
    let url = url_editar.replace('0', id_edicion)
    fetch(url, {
        headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest',
        },
        body: new FormData(formulario),
        method: "POST"
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            let fila = [];

            let re = /(?:\.([^.]+))?$/;

            let extensionesValidas = ['jpg', 'png', 'jpeg']

            // Tomamos todos los datos editados
            for (const clave in data) {
                if (clave !== "status") {
                    if (extensionesValidas.some(extension => extension === re.exec(data[clave])[1])){
                        console.log('Hola');
                        fila.unshift(`
                                <td>
                                    <span data-bs-toggle="modal" data-bs-target="#infoModal" onclick="mostrarImagen('/media/${data[clave]}')">
                                        <a href="#">${data[clave]}</a>
                                    </span>
                                </td>
                            `);
                    } else {
                        fila.unshift(data[clave]);
                    }

                }
            }

            // Agregar botones de acción
            fila.unshift(`
                <button class='bj-btn bj-btn-info bj-btn-sm' id="btn-editar" data-bs-toggle="modal" data-bs-target="#formModal" title="Editar">
                    <i class="fas fa-edit"></i>
                </button>
                <button class='bj-btn bj-btn-danger bj-btn-sm' id="btn-eliminar" data-value="${data.id}" title="Eliminar">
                    <i class="fas fa-trash"></i>
                </button>
            `);
            
            fila.reverse();
            
            // Actualizar la fila en la tabla
            tableInstance.row(fila_edicion).data(fila).draw(false);
            
            // Cerrar modal correctamente
            cerrarModalCorrectamente('formModal');
            
            // Mensaje de éxito opcional
            console.log('Registro actualizado correctamente');
            Swal.fire({
                title: '¡Éxito!',
                text: 'Se ha editado correctamente',
                icon: 'success',
            });
        } else if (data.status === 'error' && data.type == 'form_invalid'){
            document.getElementById('btnGuardarForm').disabled = false;

            // Construir el html con los errores
            let errorMessage = '<ul>';
            for (const [field, messages] of Object.entries(data.errors)) {
                errorMessage += `<li><strong>Campo ${field}:</strong> ${messages.join(', ')}</li>`;
            }
            errorMessage += '</ul>';
            Swal.fire({
                title: 'Error',
                html: `Error en los siguientes campos:<br>${errorMessage}`,
                icon: 'error'
            })
        } else {
            console.log('Ocurrio un error en el backend');
        }
    })
    .catch(error => {
        document.getElementById('btnGuardarForm').disabled = false
        Swal.fire({
            title: '¡Error!',
            icon: 'error',
            text: `Ha ocurrido un error inesperado\n${error}`
        });
    })

}
// ========================================
// FUNCION ELIMINAR
// ========================================
$(document).on('click', '#btn-eliminar', function(e) {
    e.preventDefault();
    e.stopPropagation();

    // Deshabilitamos el boton para evitar que se trate de eliminar mas de una vez
    this.disabled = true;
    
    // Extraer el id del registro que tiene el boton eliminar
    let id = this.dataset.value;
    let url = url_eliminar.replace('0', id)
    
    fetch(url, {
        headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest',
        },
        method: "DELETE"
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            tableInstance.rows(`#${data.id}`).remove().draw(false);
            Swal.fire({
                title: '!Éxito!',
                icon: 'success',
                text: 'El registro se ha eliminado correctamente',
            });
        } else if (data.status === "error" && data.tyoe === 'form_invalid') {
            Swal.fire({
                title: '¡Error!',
                icon: 'error',
                text: `No se ha podido eliminar el registro\n${data.error}`
            });
        } else {
            console.log('Error en el backend');
        }
    })
    .catch(error => {
        Swal.fire({
            title: '¡Error!',
            icon: 'error',
            text: `Ha ocurrido un error inesperado\n${error}`
        });
    });
});

// ========================================
// BOTÓN EDITAR - FUNCIONA CON RESPONSIVE
// ========================================
$(document).on('click', '#btn-editar', function(e) {
    e.preventDefault();
    e.stopPropagation();

    // Cuando se este editando actualizar el link de la foto no sera necesario
    const inputImagen = document.querySelector('input[name="link_imagen"]');
    if (inputImagen) {
        inputImagen.removeAttribute('required');
        
    }

    // Obtener la fila actual
    fila_edicion = $(this).attr('data-row-index');

    const boton = $(this);
    let datos = null;
    let fila = null;
    
    // Método 1: Intentar por TR directo
    let tr = boton.closest('tr');
    if (tr.hasClass('child')) {
        tr = tr.prev('tr');
    }
    
    if (tr.length) {
        try {
            datos = tableInstance.row(tr).data();
            if (datos) {
                fila = tr;
                console.log('✅ Método TR directo funcionó');
            }
        } catch(e) {}
    }
    
    // Método 2: Si no funcionó, buscar en todos los nodos
    if (!datos) {
        const botonDOM = boton[0];
        tableInstance.rows().every(function() {
            const node = this.node();
            const $node = $(node);
            
            // Buscar en la fila principal
            if ($node.find(botonDOM).length > 0) {
                datos = this.data();
                fila = $node;
                console.log('✅ Método búsqueda en nodos funcionó');
                return false;
            }
            
            // Buscar en fila child (responsive)
            const $next = $node.next();
            if ($next.hasClass('child') && $next.find(botonDOM).length > 0) {
                datos = this.data();
                fila = $node;
                console.log('✅ Método búsqueda en child funcionó');
                return false;
            }
        });
    }
    
    // Método 3: Si aún no hay datos, intentar por índice
    if (!datos) {
        const allRows = tableInstance.rows().nodes().to$();
        allRows.each(function(index) {
            const $row = $(this);
            if ($row.find(boton).length > 0 || 
                ($row.next().hasClass('child') && $row.next().find(boton).length > 0)) {
                datos = tableInstance.row(index).data();
                fila = $row;
                console.log('✅ Método por índice funcionó');
                return false;
            }
        });
    }
    
    if (datos) {
        fila_edicion = fila;
        id_edicion = datos[0];
        
        // Cargar datos en formulario...
        // Tu código aquí
    } else {
        console.error('❌ No se pudieron obtener los datos');
        alert('Error al obtener los datos. Por favor, recargue la página.');
    }
    
    // IMPORTANTE: Usar la API de DataTables para obtener TODOS los datos
    // incluso los que están ocultos por el responsive
    const datosCompletos = tableInstance.row(fila_edicion).data();

    // El primer elemento es el ID
    id_edicion = datosCompletos[0];
    
    // Obtener todos los campos del formulario
    const campos = $('#formulario').find('input, textarea, select').not('[type="hidden"]').not('[type="password"]');
    
    // Mapear datos a campos (empezando desde índice 1 porque 0 es el ID)
    let indiceDato = 1;
    
    campos.each(function() {
        // Excluir la última columna que son los botones
        if (indiceDato < datosCompletos.length - 1) {
            // Obtener el valor limpio (sin HTML)
            let valor = datosCompletos[indiceDato];
            
            // Si el valor tiene HTML, extraer solo el texto
            if (typeof valor === 'string' && valor.includes('<')) {
                valor = $(valor).text().trim();
            } else {
                valor = String(valor).trim();
            }
            
            // Asignar valor según tipo de campo
            if (this.tagName === 'SELECT') {
                const $select = $(this);
                // Intentar por texto primero
                let encontrado = false;
                $select.find('option').each(function() {
                    if ($(this).text().trim() === valor) {
                        $select.val($(this).val());
                        encontrado = true;
                        return false;
                    }
                });
                // Si no encontró por texto, intentar por valor
                if (!encontrado) {
                    $select.val(valor);
                }
            } else if (this.type === 'number') {
                // Limpiar caracteres no numéricos
                this.value = valor.replace(/[^0-9.-]/g, '');
            } else if (this.type === 'text' || this.type === 'textarea' || this.type === 'email'){
                this.value = valor;
            }
            
            indiceDato++;
        }
    });
    
    // Cambiar a modo edición
    modoEdicion = true;
    
    // Actualizar UI
    document.getElementById("formModalLabel").innerHTML = `
        <i class="fas fa-edit"></i>
        Editar ${seccion}
    `;
    document.getElementById("btnGuardarForm").textContent = `Actualizar ${seccion}`;
    
    console.log('Editando registro ID:', id_edicion);
});

function actualizarSelectFormularioLimpio(modelo, texto, valor) {
    // Crear un contenedor temporal
    const temp = document.createElement('div');
    temp.innerHTML = formularioLimpio;
    
    // Buscar el select específico
    const select = temp.querySelector(`#id_${modelo}`);
    
    if (select) {
        // Crear y agregar la nueva opción
        const option = document.createElement('option');
        option.value = valor;
        option.text = texto;
        select.appendChild(option);
        
        // Actualizar formularioLimpio con el nuevo HTML
        formularioLimpio = temp.innerHTML;
    }
}



// ========================================
// FIX ADICIONAL PARA PREVENIR ERRORES
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    // Prevenir que el foco quede atrapado en elementos ocultos
    document.addEventListener('focusin', function(e) {
        const modal = e.target.closest('.modal');
        if (modal && modal.getAttribute('aria-hidden') === 'true') {
            e.preventDefault();
            document.body.focus();
        }
    });
    const submenuToggles = document.querySelectorAll('.submenu-toggle');
    
    submenuToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            const parent = this.closest('.menu-item');
            const isOpen = parent.classList.contains('open');
            
            console.log('Toggle submenu:', isOpen ? 'Cerrar' : 'Abrir');
            
            parent.classList.toggle('open');
        });
    });
});

//=================================
// FUNCION FORMULARIOS ADICIONALES
//=================================

$(document).on('click', "#formAdicional", function(e){

    let datosCrudos = this.dataset.value;

    // Limpiar y convertir comillas simples a dobles, remover la parte problemática del formulario
    let datosLimpios = datosCrudos
    .replace(/'/g, '"')  // Cambiar comillas simples por dobles
    .replace(/, 'formulario':[^,}]+/, '')  // Remover la parte del formulario que no es JSON válido
    .replace(/,(\s*})/, '$1');  // Limpiar comas extra

    let objeto = JSON.parse(datosLimpios);

    console.log(objeto)
    //tomar el formulario existente
    formularioOriginal = guardarFormularioConValores();

    // remplazar formulario
    formulario.innerHTML = `${objeto.formulario}
    <div class="modal-footer">
        <button type="button" class="bj-btn bj-btn-secondary" id="regresarFormulario">Regresar</button>
        <button type="submit" class="bj-btn bj-btn-primary" id="btnGuardarForm" data-modelo="${objeto.nombre.toLowerCase()}" value="${objeto.url}" agregarfila="false">Guardar ${objeto.nombre}</button>
    </div>
    `
    // Cambiar titulo
    document.getElementById("formModalLabel").innerHTML = `
    <i class="fas fa-plus"></i>
    Agregar ${objeto.nombre}
    `
    
});

// =================================
//  Regresar al formulario original
// =================================
$(document).on('click', '#regresarFormulario', function(e){
    formulario.innerHTML = formularioOriginal;
    // Cambiar el titulo original segun si se estaba editando un registro o se estaba creando uno nuevo
    document.getElementById("formModalLabel").innerHTML = modoEdicion ? 
    `
    <i class="fas fa-edit"></i>
    Editar ${seccion}
    `
    :`
    <i class="fas fa-plus"></i>
    Agregar ${seccion}
    `
})

function guardarFormularioConValores() {
    
    // Fijar todos los valores en el HTML
    formulario.querySelectorAll('input, select, textarea').forEach(campo => {
        if (campo.type === 'checkbox' || campo.type === 'radio') {
            campo.checked ? campo.setAttribute('checked', 'checked') : campo.removeAttribute('checked');
        } else {
            campo.setAttribute('value', campo.value);
            if (campo.tagName === 'TEXTAREA') campo.innerHTML = campo.value;
            if (campo.tagName === 'SELECT') {
                [...campo.options].forEach(opt => 
                    opt.selected ? opt.setAttribute('selected', 'selected') : opt.removeAttribute('selected')
                );
            }
        }
    });
    
    return formulario.outerHTML;
}

function mostrarImagen(linkImagen) {
    document.getElementById('modalImagen').src=linkImagen;

}