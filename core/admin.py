from django.contrib import admin
from .models import UserRole, Proveedor, Producto, Venta, CompraProveedor


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email')


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre_empresa', 'cif', 'telefono', 'email', 'descuento_porcentaje', 'activo')
    list_filter = ('activo', 'ciudad', 'created_at')
    search_fields = ('nombre_empresa', 'cif', 'email')
    fieldsets = (
        ('Información General', {
            'fields': ('nombre_empresa', 'cif', 'persona_contacto')
        }),
        ('Contacto', {
            'fields': ('telefono', 'email', 'direccion', 'ciudad', 'codigo_postal', 'pais')
        }),
        ('Facturación', {
            'fields': ('descuento_porcentaje', 'iva')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'numero_referencia', 'categoria', 'proveedor', 'stock_actual', 'precio_venta', 'activo', 'alertar_stock_bajo')
    list_filter = ('categoria', 'proveedor', 'activo', 'created_at')
    search_fields = ('nombre', 'numero_referencia', 'descripcion')
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'numero_referencia', 'descripcion', 'categoria')
        }),
        ('Proveedor', {
            'fields': ('proveedor',)
        }),
        ('Precios', {
            'fields': ('precio_compra', 'precio_venta')
        }),
        ('Stock', {
            'fields': ('stock_actual', 'stock_minimo', 'ubicacion_almacen')
        }),
        ('Características', {
            'fields': ('color', 'especificaciones', 'imagen')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('numero_venta', 'producto', 'cliente', 'cantidad', 'total_neto', 'estado', 'fecha_venta')
    list_filter = ('estado', 'producto__categoria', 'fecha_venta')
    search_fields = ('numero_venta', 'cliente__username', 'producto__nombre')
    fieldsets = (
        ('Información de Venta', {
            'fields': ('numero_venta', 'cliente', 'estado')
        }),
        ('Producto', {
            'fields': ('producto', 'cantidad', 'precio_unitario')
        }),
        ('Descuento', {
            'fields': ('descuento_aplicado',)
        }),
    )
    readonly_fields = ('fecha_venta', 'created_at', 'updated_at')


@admin.register(CompraProveedor)
class CompraProveedorAdmin(admin.ModelAdmin):
    list_display = ('numero_factura', 'proveedor', 'producto', 'cantidad', 'total_neto', 'estado', 'fecha_compra')
    list_filter = ('estado', 'proveedor', 'fecha_compra')
    search_fields = ('numero_factura', 'proveedor__nombre_empresa', 'producto__nombre')
    fieldsets = (
        ('Información de Compra', {
            'fields': ('numero_factura', 'proveedor', 'estado')
        }),
        ('Producto', {
            'fields': ('producto', 'cantidad', 'precio_unitario')
        }),
        ('Fechas', {
            'fields': ('fecha_compra', 'fecha_recepcion')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
