# Documentación - Sistema de Gestión de Suministros Informáticos

## Descripción General

Este proyecto es una **aplicación web de gestión de suministros informáticos** desarrollada con **Django** (Python) que permite a una empresa:

1. **Gestionar Inventario** - Productos con stock, alertas automáticas al 90%
2. **Administrar Proveedores** - Base de datos de proveedores con facturación
3. **Registrar Ventas** - Sistema de ventas con facturación e IVA
4. **Control de Acceso** - Sistema de login con roles (Admin, Cliente, Vendedor)
5. **Reportes y Estadísticas** - Gráficas y estadísticas de ventas y beneficios

## Requisitos Cumplidos

✅ **Base de datos** - SQLite con modelos relacionales complejos
✅ **POO** - Estructura orientada a objetos con Django
✅ **Framework** - Django (framework web de Python)
✅ **Login y Roles** - Sistema de autenticación con 3 roles (Admin, Cliente, Vendedor)
✅ **Gestión de Inventario** - Alertas de stock bajo al 90%
✅ **Gestión de Proveedores** - Base de datos con contacto, facturación y descuentos
✅ **Reportes** - Estadísticas de ventas, productos populares, stock bajo
✅ **UX Intuitiva** - Interfaz sencilla, clara y fácil de usar

## Estructura del Proyecto

```
django_prueba/
├── core/                          # App principal
│   ├── models.py                  # Modelos: Proveedor, Producto, Venta, CompraProveedor, UserRole
│   ├── views.py                   # Vistas para login, dashboard, productos, proveedores, reportes
│   ├── forms.py                   # Formularios para CRUD
│   ├── admin.py                   # Configuración del admin
│   ├── auth.py                    # Utilidades de autenticación
│   ├── database.py                # Utilidades de base de datos
│   ├── templates/
│   │   └── core/
│   │       ├── base.html          # Template base
│   │       ├── login.html         # Página de login
│   │       ├── register.html      # Página de registro
│   │       ├── dashboard.html     # Dashboard principal
│   │       ├── productos/
│   │       │   └── lista.html     # Catálogo de productos
│   │       ├── proveedores/
│   │       │   └── lista.html     # Listado de proveedores
│   │       ├── ventas/
│   │       │   └── lista.html     # Historial de ventas
│   │       └── reportes.html      # Reportes y estadísticas
│   └── static/
│       └── core/
│           ├── css/
│           │   └── style.css      # Estilos (CSS moderno, responsive)
│           └── js/
│               └── main.js        # Funciones JavaScript
├── mysite/
│   ├── settings.py                # Configuración (base de datos, apps, etc.)
│   ├── urls.py                    # Enrutamiento URL
│   ├── wsgi.py
│   └── asgi.py
├── manage.py                      # Herramienta de Django
├── db.sqlite3                     # Base de datos SQLite
├── requirements.txt               # Dependencias Python
├── README.md                      # Documentación general
└── DOCUMENTACION.md               # Este archivo

```

## Modelos de Datos

### 1. **UserRole** (Rol de Usuario)
- Usuario con rol asignado (Admin, Cliente, Vendedor)
- Control de acceso a funciones según rol

### 2. **Proveedor**
- Nombre empresa, CIF, contacto, teléfono, email, dirección
- Descuento porcentaje, IVA
- Contacto principal

### 3. **Producto**
- Nombre, referencia única, descripción, categoría
- Proveedor (FK)
- Precio de compra, precio de venta
- Stock actual, stock mínimo
- Ubicación en almacén, color, especificaciones
- Imagen del producto
- **Función de Alerta**: `alertar_stock_bajo()` - Retorna True si stock ≤ 10% del stock mínimo
- **Cálculo de Margen**: `margen_beneficio()` - Calcula porcentaje de ganancia

### 4. **Venta**
- Número de venta único
- Cliente (FK a User)
- Producto (FK)
- Cantidad, precio unitario, descuento
- Estado (Pendiente, Completada, Cancelada)
- **Métodos de Cálculo**:
  - `total_bruto()` - Cantidad × Precio
  - `total_descuento()` - Aplicar descuento
  - `total_neto()` - Bruto - Descuento
  - `total_con_iva()` - Incluir IVA del proveedor

### 5. **CompraProveedor**
- Número de factura único
- Proveedor (FK)
- Producto (FK)
- Cantidad, precio unitario
- Estado (Pendiente, Recibida, Cancelada)
- Fecha de compra y recepción
- **Métodos similares a Venta para cálculos**

## Funcionalidades Principales

### 1. **Autenticación y Autorización**
- Login/Logout
- Registro de nuevos usuarios (por defecto Cliente)
- Sistema de roles:
  - **Admin**: Acceso completo a inventario, proveedores, reportes
  - **Cliente**: Ver catálogo, historial de compras
  - **Vendedor**: Acceso a inventario y proveedores (sin crear)

### 2. **Dashboard**
- **Para Admin**:
  - Estadísticas: Total de productos, proveedores, stock bajo, ventas
  - Acciones rápidas: Crear producto, crear proveedor, ver reportes
- **Para Cliente**:
  - Últimas compras
  - Acceso a catálogo y menu de navegación

### 3. **Gestión de Productos**
- Listar productos con búsqueda y filtros
- Filtrar por categoría, búsqueda por nombre/referencia
- Mostrar productos con stock bajo (⚠️ alerta visual)
- Vista detallada con margen de beneficio
- Crear/Editar productos (solo Admin)
- Imágenes de productos

### 4. **Gestión de Proveedores**
- Listar proveedores activos
- Búsqueda por nombre/email
- Ver detalles: contacto, facturación, descuentos, productos
- Crear proveedores (solo Admin)
- Gestión de facturación: descuentos, IVA

### 5. **Reportes y Estadísticas**
- **Productos con Stock Bajo** - Alerta roja para compras urgentes
- **Productos Más Vendidos** - Top 10 productos
- **Ventas por Categoría** - Estadísticas de ventas
- (Extensible con gráficas usando Chart.js)

### 6. **Sistema de Alertas**
- Productos al 90% de stock mínimo se marcan automáticamente
- Indicador visual en el catálogo
- Listado en reportes

## Roles y Permisos

| Función | Admin | Cliente | Vendedor |
|---------|-------|---------|----------|
| Ver Catálogo | ✅ | ✅ | ✅ |
| Crear Producto | ✅ | ❌ | ❌ |
| Editar Producto | ✅ | ❌ | ❌ |
| Ver Proveedores | ✅ | ❌ | ✅ |
| Crear Proveedor | ✅ | ❌ | ❌ |
| Ver Reportes | ✅ | ❌ | ❌ |
| Ver Panel Admin | ✅ | ❌ | ❌ |
| Ver Compras Propias | ✅ | ✅ | N/A |
| Ver Todas las Ventas | ✅ | ❌ | ✅ |

## Cómo Usar

### 1. **Instalación y Setup**
```bash
# Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Crear base de datos e instalar migraciones
python manage.py migrate

# Crear superusuario (Admin)
python manage.py createsuperuser

# Ejecutar servidor de desarrollo
python manage.py runserver
```

### 2. **Acceder a la Aplicación**
- **URL**: `http://127.0.0.1:8000`
- **Admin Panel**: `http://127.0.0.1:8000/admin`

### 3. **Flujo de Uso**

**Para Administrador:**
1. Login con credenciales admin
2. Dashboard con estadísticas
3. Crear/Editar productos en "Crear Producto"
4. Gestionar proveedores
5. Ver reportes para tomar decisiones

**Para Cliente:**
1. Registrarse en la aplicación
2. Login
3. Ver catálogo de productos
4. Comprar productos (futuro: carrito)
5. Ver historial de compras

## Variables de Entorno (Opcional)

Crea un archivo `.env` en la carpeta raíz:
```
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_NAME=db.sqlite3
```

Usa `python-dotenv` para cargar en `settings.py`:
```python
from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-...')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
```

## Diseño de la Base de Datos (ERD)

```
User (Django Auth)
  ├── UserRole (1:1)
  └── Venta (1:N)

Proveedor (1:N) → Producto
  ├── Producto (1:N) → Venta
  └── CompraProveedor

Producto
  ├── Venta (1:N)
  └── CompraProveedor (1:N)
```

## Cálculos y Lógica de Negocio

### Alertas de Stock
```python
def alertar_stock_bajo(self):
    umbral = (self.stock_minimo * 10) / 100
    return self.stock_actual <= umbral
```

### Margen de Beneficio
```python
def margen_beneficio(self):
    if self.precio_compra == 0:
        return 0
    return ((self.precio_venta - self.precio_compra) / self.precio_compra) * 100
```

### Facturación con Descuentos e IVA
```python
total_bruto = cantidad × precio
descuento = total_bruto × (descuento_porcentaje / 100)
total_neto = total_bruto - descuento
iva = total_neto × (iva_porcentaje / 100)
total_con_iva = total_neto + iva
```

## Mejoras Futuras

1. **Gráficas Interactivas** - Integrar Chart.js para visualización
2. **Carrito de Compra** - Sistema de compras completo para clientes
3. **Facturación PDF** - Generar PDFs de facturas
4. **Notificaciones Email** - Alertas de stock bajo
5. **API REST** - Crear API para apps móviles
6. **Exportación de Datos** - Excel, CSV
7. **Multi-almacén** - Gestión de varios almacenes
8. **Historial de Precios** - Seguimiento de cambios
9. **2FA** - Autenticación de dos factores
10. **Auditoría** - Log de cambios en datos críticos

## Tecnologías Utilizadas

- **Backend**: Django 5.2
- **Base de Datos**: SQLite (desarrollo), PostgreSQL (producción)
- **Frontend**: HTML5, CSS3 (responsive), JavaScript
- **Autenticación**: Django Auth
- **ORM**: Django ORM
- **Formularios**: Django Forms
- **Admin**: Django Admin

## Archivos Principales

| Archivo | Descripción |
|---------|-------------|
| `core/models.py` | Definición de modelos (Producto, Proveedor, etc.) |
| `core/views.py` | Lógica de vistas (login, dashboard, CRUD) |
| `core/forms.py` | Formularios para crear/editar objetos |
| `core/admin.py` | Configuración del panel administrativo |
| `mysite/urls.py` | Enrutamiento de URLs |
| `mysite/settings.py` | Configuración del proyecto |
| `core/templates/` | Plantillas HTML |
| `core/static/` | Archivos CSS y JavaScript |

## Testing (Próximas Versiones)

```bash
# Ejecutar tests
python manage.py test core

# Con cobertura
coverage run --source='.' manage.py test core
coverage report
```

## Deployment (Producción)

Para deployar en producción:
1. Cambiar `DEBUG = False` en settings
2. Usar PostgreSQL en lugar de SQLite
3. Configurar `ALLOWED_HOSTS`
4. Usar servidor WSGI (Gunicorn)
5. Servidor web (Nginx)
6. HTTPS con certificado SSL

---

**Versión**: 1.0
**Desarrollador**: Equipo de Desarrollo
**Última Actualización**: 2025-01-30
