
"""
Vistas de la aplicación core.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from django.utils import timezone
import json                          # NUEVO: para serializar datos a JSON
import datetime                      # NUEVO: para trabajar con fechas

from .models import UserRole, Proveedor, Producto, Venta, CompraProveedor
from .forms import (
    LoginForm, RegisterForm, ProveedorForm, ProductoForm,
    VentaForm, CompraProveedorForm
)


def index(request):
    """Vista de inicio."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def login_view(request):
    """Vista de login."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Bienvenido {user.username}')
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    else:
        form = LoginForm()
    
    return render(request, 'core/login.html', {'form': form})


def register_view(request):
    """Vista de registro."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserRole.objects.create(user=user, role='cliente')
            messages.success(request, 'Cuenta creada exitosamente. Inicia sesión.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegisterForm()
    
    return render(request, 'core/register.html', {'form': form})


def logout_view(request):
    """Vista de logout."""
    logout(request)
    messages.success(request, 'Sesión cerrada exitosamente')
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
    """Dashboard principal."""
    user_role = getattr(request.user, 'role', None)
    
    context = {
        'user_role': user_role.role if user_role else 'cliente',
    }
    
    if user_role and user_role.role == 'admin':
        context.update({
            'total_productos': Producto.objects.count(),
            'total_proveedores': Proveedor.objects.count(),
            'productos_bajo_stock': Producto.objects.filter(stock_actual__lte=10).count(),
            'ventas_totales': Venta.objects.aggregate(Sum('cantidad'))['cantidad__sum'] or 0,
            'compras_totales': CompraProveedor.objects.filter(estado='recibida').aggregate(Sum('cantidad'))['cantidad__sum'] or 0,
        })
    else:
        context.update({
            'ultimas_compras': Venta.objects.filter(cliente=request.user)[:5],
        })
    
    return render(request, 'core/dashboard.html', context)


# PRODUCTOS

@login_required(login_url='login')
def lista_productos(request):
    """Lista de productos."""
    productos = Producto.objects.filter(activo=True)
    
    busqueda = request.GET.get('q', '')
    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) |
            Q(numero_referencia__icontains=busqueda)
        )
    
    categoria = request.GET.get('categoria', '')
    if categoria:
        productos = productos.filter(categoria=categoria)
    
    mostrar_bajo_stock = request.GET.get('bajo_stock', False)
    if mostrar_bajo_stock:
        productos = productos.filter(stock_actual__lte=10)
    
    context = {
        'productos': productos,
        'busqueda': busqueda,
        'categoria': categoria,
    }
    return render(request, 'core/productos/lista.html', context)


@login_required(login_url='login')
def detalle_producto(request, pk):
    """Detalle de un producto."""
    producto = get_object_or_404(Producto, pk=pk, activo=True)
    
    context = {
        'producto': producto,
        'margen_beneficio': producto.margen_beneficio(),
        'stock_bajo': producto.alertar_stock_bajo(),
    }
    return render(request, 'core/productos/detalle.html', context)


@login_required(login_url='login')
def crear_producto(request):
    """Crear nuevo producto (solo admin)."""
    if not hasattr(request.user, 'role') or request.user.role.role != 'admin':
        messages.error(request, 'No tienes permisos para realizar esta acción')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado exitosamente')
            return redirect('lista_productos')
    else:
        form = ProductoForm()
    
    return render(request, 'core/productos/form.html', {'form': form, 'titulo': 'Crear Producto'})


@login_required(login_url='login')
def editar_producto(request, pk):
    """Editar producto (solo admin)."""
    if not hasattr(request.user, 'role') or request.user.role.role != 'admin':
        messages.error(request, 'No tienes permisos para realizar esta acción')
        return redirect('dashboard')
    
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente')
            return redirect('detalle_producto', pk=producto.pk)
    else:
        form = ProductoForm(instance=producto)
    
    return render(request, 'core/productos/form.html', {'form': form, 'titulo': 'Editar Producto'})


# PROVEEDORES

@login_required(login_url='login')
def lista_proveedores(request):
    """Lista de proveedores."""
    if not hasattr(request.user, 'role') or request.user.role.role not in ['admin', 'vendedor']:
        messages.error(request, 'No tienes permisos para ver esta sección')
        return redirect('dashboard')
    
    proveedores = Proveedor.objects.filter(activo=True)
    
    busqueda = request.GET.get('q', '')
    if busqueda:
        proveedores = proveedores.filter(
            Q(nombre_empresa__icontains=busqueda) |
            Q(email__icontains=busqueda)
        )
    
    context = {
        'proveedores': proveedores,
        'busqueda': busqueda,
    }
    return render(request, 'core/proveedores/lista.html', context)


@login_required(login_url='login')
def detalle_proveedor(request, pk):
    """Detalle de un proveedor."""
    if not hasattr(request.user, 'role') or request.user.role.role not in ['admin', 'vendedor']:
        messages.error(request, 'No tienes permisos para ver esta sección')
        return redirect('dashboard')
    
    proveedor = get_object_or_404(Proveedor, pk=pk, activo=True)
    productos = proveedor.productos.filter(activo=True)
    
    context = {
        'proveedor': proveedor,
        'productos': productos,
    }
    return render(request, 'core/proveedores/detalle.html', context)


@login_required(login_url='login')
def crear_proveedor(request):
    """Crear nuevo proveedor (solo admin)."""
    if not hasattr(request.user, 'role') or request.user.role.role != 'admin':
        messages.error(request, 'No tienes permisos para realizar esta acción')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor creado exitosamente')
            return redirect('lista_proveedores')
    else:
        form = ProveedorForm()
    
    return render(request, 'core/proveedores/form.html', {'form': form, 'titulo': 'Crear Proveedor'})


# VENTAS

@login_required(login_url='login')
def lista_ventas(request):
    """Lista de ventas."""
    if hasattr(request.user, 'role') and request.user.role.role == 'cliente':
        ventas = Venta.objects.filter(cliente=request.user)
    elif hasattr(request.user, 'role') and request.user.role.role in ['admin', 'vendedor']:
        ventas = Venta.objects.all()
    else:
        messages.error(request, 'No tienes permisos para ver esta sección')
        return redirect('dashboard')
    
    estado = request.GET.get('estado', '')
    if estado:
        ventas = ventas.filter(estado=estado)
    
    context = {
        'ventas': ventas,
        'estado': estado,
    }
    return render(request, 'core/ventas/lista.html', context)


# REPORTES Y ESTADÍSTICAS

def _obtener_datos_evolucion_mensual():
    """
    Función auxiliar que calcula las ventas y compras de los últimos 12 meses.
    
    Explicación del proceso:
    1. Calculamos el mes actual y retrocedemos 11 meses para cubrir 12 meses en total.
    2. Para cada mes, consultamos la BD con filter() usando __year y __month.
    3. Devolvemos listas de etiquetas y datos listos para Chart.js.
    
    Usamos una función auxiliar (_) para mantener la vista reportes() limpia
    y poder reutilizar esta lógica si la necesitamos en otro sitio.
    """
    hoy = datetime.date.today()
    etiquetas = []   # Nombres de los meses para el eje X: ["Jun 2024", "Jul 2024"...]
    datos_ventas = []    # Unidades vendidas por mes
    datos_compras = []   # Unidades compradas por mes

    # Iteramos los últimos 12 meses empezando por el más antiguo
    for i in range(11, -1, -1):
        # Calculamos el mes correspondiente restando 'i' meses al mes actual
        # timedelta no soporta meses directamente, así que usamos replace() con aritmética
        mes = hoy.month - i
        anio = hoy.year
        # Si mes es 0 o negativo, retrocedemos un año y ajustamos el mes
        while mes <= 0:
            mes += 12
            anio -= 1

        # Creamos la etiqueta del eje X con el nombre del mes abreviado
        fecha_ref = datetime.date(anio, mes, 1)
        etiquetas.append(fecha_ref.strftime("%b %Y"))  # Ej: "Ene 2025"

        # Consultamos la BD: sum de cantidades en ese año y mes concretos
        ventas_mes = Venta.objects.filter(
            fecha_venta__year=anio,
            fecha_venta__month=mes,
            estado='completada'  # Solo ventas completadas, no pendientes ni canceladas
        ).aggregate(total=Sum('cantidad'))['total'] or 0

        compras_mes = CompraProveedor.objects.filter(
            fecha_compra__year=anio,
            fecha_compra__month=mes,
            estado='recibida'
        ).aggregate(total=Sum('cantidad'))['total'] or 0

        datos_ventas.append(int(ventas_mes))
        datos_compras.append(int(compras_mes))

    return etiquetas, datos_ventas, datos_compras


@login_required(login_url='login')
def reportes(request):
    """Vista de reportes y estadísticas."""
    if not hasattr(request.user, 'role') or request.user.role.role != 'admin':
        messages.error(request, 'No tienes permisos para ver reportes')
        return redirect('dashboard')
    
    # --- Datos existentes ---
    ventas_por_categoria = Venta.objects.values('producto__categoria').annotate(
        total=Sum('cantidad'),
        ingresos=Sum('cantidad')
    ).order_by('-total')
    
    productos_populares = Producto.objects.annotate(
        vendidas=Count('venta')
    ).filter(vendidas__gt=0).order_by('-vendidas')[:10]
    
    productos_bajo_stock = Producto.objects.filter(stock_actual__lte=10)

    # --- NUEVO: datos para la gráfica de evolución mensual ---
    etiquetas, datos_ventas, datos_compras = _obtener_datos_evolucion_mensual()

    # json.dumps() convierte la lista Python a una cadena JSON válida para JavaScript
    # Ejemplo: ["Ene 2025", "Feb 2025"] → '["Ene 2025", "Feb 2025"]'
    # ensure_ascii=False permite caracteres como tildes y ñ sin escapar
    context = {
        'ventas_por_categoria': ventas_por_categoria,
        'productos_populares': productos_populares,
        'productos_bajo_stock': productos_bajo_stock,

        # Pasamos los datos como JSON para que JavaScript pueda leerlos directamente
        'grafica_etiquetas': json.dumps(etiquetas, ensure_ascii=False),
        'grafica_ventas': json.dumps(datos_ventas),
        'grafica_compras': json.dumps(datos_compras),
    }
    return render(request, 'core/reportes.html', context)