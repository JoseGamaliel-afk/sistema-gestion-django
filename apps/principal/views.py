from django.shortcuts import render
from django.views import View


# ===============================
# 🔹 PRINCIPAL 1.1 - VENTAS
# ===============================
class Principal11View(View):
    """Vista Principal 1.1 - Gestión de Ventas"""
    template_name = 'principal/principal11.html'

    def get(self, request):
        ventas = [
            {'id': 1, 'cliente': 'Juan Pérez', 'producto': 'Laptop HP', 'cantidad': 2, 'total': 3500000, 'fecha': '2024-01-15', 'estado': 'Completada'},
            {'id': 2, 'cliente': 'María García', 'producto': 'Monitor LG 27"', 'cantidad': 1, 'total': 850000, 'fecha': '2024-01-14', 'estado': 'Pendiente'},
            {'id': 3, 'cliente': 'Carlos López', 'producto': 'Teclado Mecánico', 'cantidad': 3, 'total': 450000, 'fecha': '2024-01-13', 'estado': 'Completada'},
            {'id': 4, 'cliente': 'Ana Martínez', 'producto': 'Mouse Inalámbrico', 'cantidad': 5, 'total': 250000, 'fecha': '2024-01-12', 'estado': 'Cancelada'},
            {'id': 5, 'cliente': 'Pedro Sánchez', 'producto': 'Webcam HD', 'cantidad': 2, 'total': 180000, 'fecha': '2024-01-11', 'estado': 'Completada'},
        ]

        context = {
            'ventas': ventas,
            'total_ventas': len(ventas),
            'ventas_completadas': len([v for v in ventas if v['estado'] == 'Completada']),
            'ventas_pendientes': len([v for v in ventas if v['estado'] == 'Pendiente']),
            'breadcrumbs': [
                {'nombre': 'Principal 1', 'url': None},
                {'nombre': 'Gestión de Ventas', 'url': None}
            ]
        }

        return render(request, self.template_name, context)


# ===============================
# 🔹 PRINCIPAL 1.2 - REPORTES
# ===============================
class Principal12View(View):
    """Vista Principal 1.2 - Reportes"""
    template_name = 'principal/principal12.html'

    def get(self, request):
        reportes = [
            {'id': 1, 'nombre': 'Ventas Mensuales', 'tipo': 'Ventas', 'fecha': '2024-01-15', 'estado': 'Generado'},
            {'id': 2, 'nombre': 'Inventario Actual', 'tipo': 'Inventario', 'fecha': '2024-01-14', 'estado': 'Pendiente'},
            {'id': 3, 'nombre': 'Clientes Activos', 'tipo': 'Clientes', 'fecha': '2024-01-13', 'estado': 'Generado'},
            {'id': 4, 'nombre': 'Productos Agotados', 'tipo': 'Inventario', 'fecha': '2024-01-12', 'estado': 'Generado'},
            {'id': 5, 'nombre': 'Facturación Semanal', 'tipo': 'Facturación', 'fecha': '2024-01-11', 'estado': 'Generado'},
        ]

        context = {
            'reportes': reportes,
            'total_reportes': len(reportes),
            'reportes_generados': len([r for r in reportes if r['estado'] == 'Generado']),
            'breadcrumbs': [
                {'nombre': 'Principal 1', 'url': None},
                {'nombre': 'Reportes', 'url': None}
            ]
        }

        return render(request, self.template_name, context)


# ===============================
# 🔹 PRINCIPAL 2.1 - INVENTARIO
# ===============================
class Principal21View(View):
    """Vista Principal 2.1 - Gestión de Inventario"""
    template_name = 'principal/principal21.html'

    def get(self, request):
        productos = [
            {'codigo': 'P001', 'nombre': 'Laptop HP', 'categoria': 'Tecnología', 'stock': 10, 'stock_minimo': 5, 'precio': 3500000, 'estado': 'Disponible'},
            {'codigo': 'P002', 'nombre': 'Mouse Inalámbrico', 'categoria': 'Accesorios', 'stock': 2, 'stock_minimo': 5, 'precio': 50000, 'estado': 'Stock Bajo'},
            {'codigo': 'P003', 'nombre': 'Teclado Mecánico', 'categoria': 'Accesorios', 'stock': 0, 'stock_minimo': 5, 'precio': 120000, 'estado': 'Agotado'},
            {'codigo': 'P004', 'nombre': 'Monitor LG 27"', 'categoria': 'Tecnología', 'stock': 7, 'stock_minimo': 3, 'precio': 850000, 'estado': 'Disponible'},
        ]

        context = {
            'productos': productos,
            'total_productos': len(productos),
            'productos_disponibles': len([p for p in productos if p['estado'] == 'Disponible']),
            'productos_stock_bajo': len([p for p in productos if p['estado'] == 'Stock Bajo']),
            'productos_agotados': len([p for p in productos if p['estado'] == 'Agotado']),
            'breadcrumbs': [
                {'nombre': 'Principal 2', 'url': None},
                {'nombre': 'Inventario', 'url': None}
            ]
        }

        return render(request, self.template_name, context)


# ===============================
# 🔹 PRINCIPAL 2.2 - CLIENTES
# ===============================
class Principal22View(View):
    """Vista Principal 2.2 - Gestión de Clientes"""
    template_name = 'principal/principal22.html'

    def get(self, request):
        clientes = [
            {'nombre': 'Juan Pérez', 'documento': '12345678', 'email': 'juan@email.com', 'ciudad': 'Bogotá', 'tipo': 'Premium', 'compras': 15, 'estado': 'Activo'},
            {'nombre': 'María García', 'documento': '87654321', 'email': 'maria@email.com', 'ciudad': 'Medellín', 'tipo': 'Regular', 'compras': 8, 'estado': 'Activo'},
            {'nombre': 'Carlos López', 'documento': '45678912', 'email': 'carlos@email.com', 'ciudad': 'Cali', 'tipo': 'Nuevo', 'compras': 2, 'estado': 'Inactivo'},
            {'nombre': 'Ana Martínez', 'documento': '78912345', 'email': 'ana@email.com', 'ciudad': 'Barranquilla', 'tipo': 'Premium', 'compras': 20, 'estado': 'Activo'},
        ]

        context = {
            'clientes': clientes,
            'total_clientes': len(clientes),
            'clientes_activos': len([c for c in clientes if c['estado'] == 'Activo']),
            'clientes_premium': len([c for c in clientes if c['tipo'] == 'Premium']),
            'total_ventas': sum([c['compras'] * 100000 for c in clientes]),
            'breadcrumbs': [
                {'nombre': 'Principal 2', 'url': None},
                {'nombre': 'Clientes', 'url': None}
            ]
        }

        return render(request, self.template_name, context)