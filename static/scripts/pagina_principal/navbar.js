// esta variable es para evitar que se spameem muchas peticiones
let timer

// ========================================
// FUNCIONES DEL HEADER
// ========================================

// Cambiar estilo del header al hacer scroll
window.addEventListener('scroll', function() {
    const header = document.getElementById('header');
    if (window.scrollY > 100) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
});

// Toggle del menú móvil
const navMenu = document.getElementById('nav-menu');
if (navMenu) navMenu.classList.remove('active');

// ========================================
// FUNCIONES DE NAVEGACIÓN
// ========================================

// Scroll suave a la sección de productos
function scrollToProducts() {
    document.getElementById('productos').scrollIntoView({ 
        behavior: 'smooth' 
    });
}


// ========================================
// SISTEMA DE NOTIFICACIONES
// ========================================

// Mostrar notificación
// function showNotification(message) {
//     // Crear elemento de notificación
//     const notification = document.createElement('div');
//     notification.style.cssText = `
//         position: fixed;
//         top: 100px;
//         right: 20px;
//         background: linear-gradient(45deg, #dc3545, #28a745);
//         color: white;
//         padding: 1rem 2rem;
//         border-radius: 10px;
//         z-index: 10000;
//         font-weight: bold;
//         box-shadow: 0 8px 25px rgba(220, 53, 69, 0.4);
//         transform: translateX(400px);
//         transition: all 0.3s ease;
//     `;
//     notification.textContent = message;
    
    // Agregar al DOM
    // document.body.appendChild(notification);
    
    // Animar entrada
//     setTimeout(() => {
//         notification.style.transform = 'translateX(0)';
//     }, 100);
    
//     // Remover después de 3 segundos
//     setTimeout(() => {
//         notification.style.transform = 'translateX(400px)';
//         setTimeout(() => {
//             document.body.removeChild(notification);
//         }, 300);
//     }, 3000);
// }

// ========================================
// ANIMACIONES DE SCROLL
// ========================================

// Observer para animaciones al hacer scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }
    });
}, observerOptions);

// Observar todos los elementos con clase 'fade-in'
document.addEventListener('DOMContentLoaded', function() {
    const fadeElements = document.querySelectorAll('.fade-in');
    fadeElements.forEach(element => {
        observer.observe(element);
    });
});

// ========================================
// EFECTOS ADICIONALES Y INTERACTIVIDAD
// ========================================

// Efecto parallax en el hero
window.addEventListener('scroll', function() {
    const scrolled = window.pageYOffset;
    const hero = document.querySelector('.hero');
    const rate = scrolled * -0.5;
    
    if (hero) {
        hero.style.transform = `translateY(${rate}px)`;
    }
});

// Animación de hover en las tarjetas de productos
document.addEventListener('DOMContentLoaded', function() {
    const productCards = document.querySelectorAll('.product-card');
    
    productCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
});

// Función para smooth scroll en los enlaces del nav
document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            
            if (targetId.startsWith('#')) {
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
            
            // Cerrar menú móvil si está abierto
            const navMenu = document.getElementById('nav-menu');
            navMenu.classList.remove('active');
        });
    });
});

// Efecto de typing en el título del hero (opcional)
function typeWriter(element, text, speed = 100) {
    let i = 0;
    element.innerHTML = '';
    
    function type() {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    type();
}

// Inicializar efectos cuando la página carga
window.addEventListener('load', function() {
    // Pequeño delay para que se vea el efecto
    setTimeout(() => {
        const heroTitle = document.querySelector('.hero-title');
        if (heroTitle) {
            typeWriter(heroTitle, 'BOX JEANS URBAN', 150);
        }
    }, 500);
});



let showCart = () => {
    window.location.href = "carrito/"
}
// ========================================
// MINI CARRITO
// ========================================


function cargarMiniCarrito() {
    
    fetch('/carrito/json/')
        .then(r => r.json())
        .then(data => {
            const container = document.getElementById('miniCartItems');
            const badge     = document.getElementById('cartBadge');
            const total     = document.getElementById('miniCartTotal');
            const count     = document.getElementById('miniCartCount');

            badge.textContent = data.items.length;
            count.textContent = data.items.length;
            total.textContent = window.formatPrice(data.total);

            if (data.items.length === 0) {
                container.innerHTML = '<p class="cart-empty">Tu carrito está vacío</p>';
                return;
            }

            container.innerHTML = data.items.map(item => `
                <div class="cart-item-mini" id="item-${item.id}">
                    <input type="checkbox" class="item-check" ${item.seleccionado?'checked':''} data-producto-id="${item.producto_id}">
                    <img class="cart-item-img"
                        src="/media/${item.imagen}"
                        onerror="this.src='/static/img/Imagen_no_encontrada.svg'"
                        alt="${item.nombre}">
                    <div class="cart-item-info">
                        <div class="cart-item-name">${item.nombre}</div>
                        <div class="cart-item-meta">Talla: ${item.talla || 'N/A'}</div>
                        <div class="cart-item-price" data-precio='${item.precio}'>${window.formatPrice(item.precio)}</div>
                        <div class="cart-item-qty">
                            <div class="quantity-controls">
                                <span class="qty-label">Qty</span>
                                <input 
                                    type="number" 
                                    class="qty-number" 
                                    id="qty-${item.id}"
                                    
                                    value="${item.cantidad}"
                                    min="1" 
                                    max="${item.cant_max}"
                                    data-item-id="${item.id}"
                                    style="width:60px; text-align:center; background:transparent; border:none; color:inherit; font-size:inherit; font-weight:inherit;"
                                >
                            </div>
                            <button class="remove-btn" onclick="eliminarItem('${item.id}', '${item.nombre}')" title="Eliminar"><i class="fas fa-trash"></i></button>
                        </div>
                        <div class="item-error" id="error-${item.id}"></div>
                    </div>
                </div>
            `).join('');



            // Select All
            document.getElementById('selectAll').addEventListener('change', function() {
                document.querySelectorAll('.item-check').forEach(cb => cb.checked = this.checked);
                
                clearTimeout(timer);
                timer = setTimeout(() => {
                    window.seleccionarItem(null, null, this.checked);
                    actualizarTotal();
                }, 600)
            });
            // Funcion para guardar la cantidad de un producto cada cierto tiempo

            document.querySelectorAll('.qty-number').forEach(input => {
                input.addEventListener('input', function() {
                    clearTimeout(timer);
                    timer = setTimeout(() => {
                        // hace la petición solo después de 600ms sin escribir
                        
                        window.actualizarCantidad(this.dataset.itemId, this.value)
                        .then(data => {
                            if (data.status == 'success'){
                                actualizarTotal(data.total);
                            } else if (data.status = 'error'){
                                mostrarErrorItem(data.id, data.message);
                            }   
                        });
                        
                    }, 600)
                })
            });

            // Funcion para seleccionar lo productos que seran comprados
            document.querySelectorAll('.item-check').forEach(check => {
                check.addEventListener('change', function(e) {

                    clearTimeout(timer);
                    timer = setTimeout(() => {

                        window.seleccionarItem(this.dataset.productoId, e.target.checked?true:false)
                        actualizarTotal()
                    }, 600)
                })
            });
        })
        // .catch(() => {
        //     document.getElementById('miniCartItems').innerHTML =
        //         '<p class="cart-empty">Error al cargar el carrito</p>';
        // });
}

// Actualizar Total del MiniCarito

let  actualizarTotal = (total) => {
    document.querySelector('.total-price').textContent = `${window.formatPrice(total)}`
}

// Funcion para eliminar item del minicarrito
let eliminarItem = (id, nombre)=>{
        if (confirm('¿Estas seguro de eliminar este producto del carrito de compras?')) {
            fetch(`eliminar_item/${id}`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(r => r.json())
            .then(data =>{
                if(data.status === "success"){
                    let item = document.getElementById(`item-${id}`);
                    item.style.animation = 'fadeOut 0.3s ease';
                    item.remove();
                    actualizarTotal();
                    const container = document.getElementById('miniCartItems').innerHTML = `
                            <p class="cart-empty">Tu carrito está vacío</p>
                    `;
                }
            })
            .catch(error => {
                Swal.fire({
                icon: "error",
                title: "Oops...",
                text: `Ocurrio un error inesperado ${error}`,
                });
            })
        }
}

document.addEventListener('DOMContentLoaded', function() {

    let carritoYaCargado = false;

    const cartWrapper = document.getElementById('cartWrapper');
    const miniCart    = document.getElementById('miniCart');
    const cartBtn     = document.getElementById('cartBtn');

    if (!cartWrapper || !miniCart) return;

    // Click al botón — abre o cierra
    cartBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        miniCart.classList.toggle('visible');

        if (!carritoYaCargado) {
            cargarMiniCarrito();
            carritoYaCargado = true;
        }
    });

    // Click afuera — cierra
    document.addEventListener('click', function(e) {
        if (!cartWrapper.contains(e.target)) {
            miniCart.classList.remove('visible');
        }
    });

});

function mostrarErrorItem(itemId, mensaje) {
    const errorDiv = document.getElementById(`error-${itemId}`);
    if (!errorDiv) return;

    errorDiv.textContent = mensaje;
    errorDiv.classList.add('visible');

    // Se oculta automáticamente después de 3 segundos
    setTimeout(() => {
        errorDiv.classList.remove('visible');
        errorDiv.textContent = '';
    }, 10000);
}

function limpiarErrorItem(itemId) {
    const errorDiv = document.getElementById(`error-${itemId}`);
    if (errorDiv) {
        errorDiv.classList.remove('visible');
        errorDiv.textContent = '';
    }
}