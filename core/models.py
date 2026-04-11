"""
Modelos de la aplicación core - Gestión de Suministros Informáticos.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Modelo base con timestamps para otros modelos.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserRole(models.Model):
    """
    Define roles de usuario en la aplicación.
    """
    ROLES_CHOICES = [
        ('admin', 'Administrador'),
        ('cliente', 'Cliente'),
        ('vendedor', 'Vendedor'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='role')
    role = models.CharField(max_length=20, choices=ROLES_CHOICES, default='cliente')
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    class Meta:
        verbose_name = "Rol de Usuario"
        verbose_name_plural = "Roles de Usuarios"


class Proveedor(TimeStampedModel):
    """
    Modelo para gestionar proveedores.
    """
    nombre_empresa = models.CharField(max_length=200)
    cif = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    direccion = models.TextField()
    ciudad = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10)
    pais = models.CharField(max_length=100)
    persona_contacto = models.CharField(max_length=200)
    descuento_porcentaje = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    iva = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=21,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nombre_empresa
    
    def facturacion_total(self):
        """Suma total de compras recibidas de este proveedor."""
        from django.db.models import Sum
        resultado = self.compras.filter(estado='recibida').aggregate(
            total=Sum('precio_unitario')
        )
        return resultado['total'] or 0

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre_empresa']


class Producto(TimeStampedModel):
    """
    Modelo para gestionar productos.
    """
    CATEGORIAS = [
        ('hardware', 'Hardware'),
        ('software', 'Software'),
        ('accesorios', 'Accesorios'),
        ('cables', 'Cables'),
        ('memorias', 'Memorias'),
        ('fuentes', 'Fuentes de Alimentación'),
        ('otros', 'Otros'),
    ]
    
    nombre = models.CharField(max_length=200)
    numero_referencia = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=50, choices=CATEGORIAS)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='productos')
    
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    
    stock_actual = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=10)
    ubicacion_almacen = models.CharField(max_length=200, blank=True)
    
    color = models.CharField(max_length=50, blank=True)
    especificaciones = models.TextField(blank=True)
    
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.nombre} ({self.numero_referencia})"
    
    def alertar_stock_bajo(self):
        """Devuelve True si el stock está al 90% o menos del stock mínimo."""
        umbral = self.stock_minimo * 0.9
        return self.stock_actual <= umbral
    
    def margen_beneficio(self):
        """Calcula el margen de beneficio en porcentaje."""
        if self.precio_compra == 0:
            return 0
        return ((self.precio_venta - self.precio_compra) / self.precio_compra) * 100
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['numero_referencia']),
            models.Index(fields=['categoria']),
        ]


class Venta(TimeStampedModel):
    """
    Modelo para registrar ventas.
    """
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]
    
    numero_venta = models.CharField(max_length=20, unique=True)
    cliente = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='ventas')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    
    descuento_aplicado = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha_venta = models.DateTimeField(auto_now_add=True)
    
    def total_bruto(self):
        return self.cantidad * self.precio_unitario
    
    def total_descuento(self):
        return (self.total_bruto() * self.descuento_aplicado) / 100
    
    def total_neto(self):
        return self.total_bruto() - self.total_descuento()
    
    def total_con_iva(self):
        iva = (self.total_neto() * self.producto.proveedor.iva) / 100
        return self.total_neto() + iva
    
    def __str__(self):
        return f"Venta {self.numero_venta} - {self.producto.nombre}"
    
    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['-fecha_venta']


class CompraProveedor(TimeStampedModel):
    """
    Modelo para registrar compras a proveedores.
    """
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('recibida', 'Recibida'),
        ('cancelada', 'Cancelada'),
    ]
    
    numero_factura = models.CharField(max_length=50, unique=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='compras')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha_compra = models.DateTimeField(auto_now_add=True)
    fecha_recepcion = models.DateTimeField(null=True, blank=True)
    
    def total_bruto(self):
        return self.cantidad * self.precio_unitario
    
    def total_descuento(self):
        return (self.total_bruto() * self.proveedor.descuento_porcentaje) / 100
    
    def total_neto(self):
        return self.total_bruto() - self.total_descuento()
    
    def total_con_iva(self):
        iva = (self.total_neto() * self.proveedor.iva) / 100
        return self.total_neto() + iva
    
    def __str__(self):
        return f"Compra {self.numero_factura} - {self.proveedor.nombre_empresa}"
    
    class Meta:
        verbose_name = "Compra a Proveedor"
        verbose_name_plural = "Compras a Proveedores"
        ordering = ['-fecha_compra']
