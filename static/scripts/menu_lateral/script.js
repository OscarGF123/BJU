// Inicialización del DataTable con configuración responsive mejorada
$(document).ready(function() {
    var datatable = $('#datatable').DataTable({
        columnDefs: [
            {
                targets: '_all',  // ← aplica a todas las columnas
                render: function(data) {
                    if (data === null || data === undefined || data === 'None' || data === '') {
                        return 'Vacio';
                    }
                    return data;
                }
            }
        ],
        responsive: {
            details: {
                type: 'inline',
                target: 'tr'
            }
        },
        order: [[0, 'asc']], //odena de manera ascendente por la primera columna
        pageLength: 10,
        lengthMenu: [[5, 10, 25, 50, -1], [5, 10, 25, 50, "Todos"]],
        language: {
            lengthMenu: "Mostrar _MENU_ registros",
            zeroRecords: "No se encontraron registros",
            info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
            infoEmpty: "No hay registros disponibles",
            infoFiltered: "(filtrado de _MAX_ registros totales)",
            search: "Buscar:",
            paginate: {
                first: "Primero",
                last: "Último",
                next: "Siguiente",
                previous: "Anterior"
            },
            processing: "Procesando...",
            emptyTable: "No hay datos disponibles en la tabla"
        },
        // Configuración adicional para mejor rendimiento en móviles
        deferRender: true,
        scrollCollapse: true,
        scroller: false,
        // Configuración de búsqueda
        searchDelay: 500,
        // Mantener el estado de la tabla
        stateSave: false,
        // Opciones de procesamiento
        processing: true,
        // Configuración responsive adicional
        autoWidth: false,
        // Callbacks para personalización
        initComplete: function() {
            
            // Agregar clases personalizadas para mejor estilo
            $('.dataTables_filter input').attr('placeholder', 'Buscar productos...');
            
            // Mejorar la accesibilidad
            $('.dataTables_filter input').attr('aria-label', 'Buscar en la tabla');
            $('.dataTables_length select').attr('aria-label', 'Número de registros por página');
        }
    });

    // Redimensionar DataTable cuando se cambia el tamaño de la ventana
    $(window).on('resize', function() {
        datatable.responsive.recalc();
    });
});

// ========================================
// FUNCIONALIDAD DEL SIDEBAR
// ========================================

function initBoxJeansDashboard() {
    const bjMenuButton = document.getElementById('bjMenu');
    const bjSidebarElement = document.getElementById('bjSidebar');
    const bjMainContent = document.getElementById('bjMain');
    const menuContainer = document.querySelector('.bj-menu-container');
    
    if (!bjMenuButton || !bjSidebarElement || !bjMainContent) {
        console.error('❌ Error: No se encontraron los elementos del dashboard');
        return;
    }
    
    // Toggle sidebar
    function toggleSidebar() {
        bjSidebarElement.classList.toggle('bj-menu-toggle');
        bjMenuButton.classList.toggle('bj-menu-toggle');
        bjMainContent.classList.toggle('bj-menu-toggle');
        
        // Recalcular responsive del DataTable después del toggle
        setTimeout(function() {
            if ($.fn.DataTable.isDataTable('#datatable')) {
                $('#datatable').DataTable().responsive.recalc();
            }
        }, 400);
    }
    
    // Event listeners
    bjMenuButton.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        toggleSidebar();
    });
    
    if (menuContainer) {
        menuContainer.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            toggleSidebar();
        });
    }
    
    // Cerrar sidebar en móvil al hacer clic fuera
    document.addEventListener('click', function(event) {
        if (window.innerWidth <= 768) {
            const isClickInsideSidebar = bjSidebarElement.contains(event.target);
            const isClickOnMenu = bjMenuButton.contains(event.target) || 
                                    (menuContainer && menuContainer.contains(event.target));
            
            if (!isClickInsideSidebar && !isClickOnMenu && 
                bjSidebarElement.classList.contains('bj-menu-toggle')) {
                toggleSidebar();
            }
        }
    });
    
}

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initBoxJeansDashboard);
} else {
    initBoxJeansDashboard();
}