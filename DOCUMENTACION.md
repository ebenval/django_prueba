# Documentación - Sistema de Gestión de Suministros Informáticos

## Descripción General

Este proyecto es una **aplicación web de gestión de suministros informáticos** desarrollada con **Django** (Python) que permite a una empresa gestionar sus productos, proveedores, ventas y clientes desde una única plataforma web.

Funcionalidades principales:

1. **Gestión de Inventario** — Productos con stock, alertas automáticas al 90% del mínimo
2. **Administración de Proveedores** — Base de datos completa con facturación, descuentos e IVA
3. **Sistema de Ventas** — Flujo completo de compra para clientes con descuento de stock automático
4. **Control de Acceso** — Sistema de login con 3 roles diferenciados (Admin, Cliente, Vendedor)
5. **Reportes y Gráficas** — Evolución mensual de ventas y compras con Chart.js
6. **Tests Automatizados** — 38 tests unitarios que cubren modelos, vistas y formularios

---

## Requisitos Mínimos Cumplidos

| Requisito | Estado | Detalle |
|-----------|--------|---------|
| Base de datos | ✅ | SQLite con 5 modelos relacionales y migraciones |
| Programación orientada a objetos | ✅ | Herencia, encapsulación, decoradores, métodos de instancia |
| Framework Django | ✅ | ORM, Forms, Admin, Templates, Management Commands |
| Sistema de login y roles | ✅ | 3 roles con decorador reutilizable `requiere_rol` |
| Documentación | ✅ | Este documento + README + docstrings en todo el código |

---

## Stack Tecnológico

| Tecnología | Versión | Uso |
|------------|---------|-----|
| Python | 3.8+ | Lenguaje principal |
| Django | 5.x | Framework web backend |
| SQLite | — | Base de datos (desarrollo) |
| Chart.js | 4.4.0 | Gráficas interactivas en frontend |
| Pillow | 10.0+ | Procesamiento de imágenes de productos |
| python-dotenv | — | Variables de entorno |
| HTML5 / CSS3 | — | Frontend responsive |
| JavaScript | ES6+ | Interactividad en templates |

---

## Estructura del Proyecto

```
django_prueba/
├── core/                               # App principal
│   ├── models.py                       # Modelos de datos
│   ├── views.py                        # Vistas (lógica de negocio)
│   ├── forms.py                        # Formularios Django
│   ├── admin.py                        # Panel administrativo
│   ├── auth.py                         # Decorador requiere_rol y utilidades
│   ├── tests.py                        # 38 tests automatizados
│   ├── management/
│   │   └── commands/
│   │       └── poblar_bd.py            # Command para datos de prueba
│   ├── templates/
│   │   └── core/
│   │       ├── base.html               # Template base con nav dinámica
│   │       ├── login.html              # Inicio de sesión
│   │       ├── register.html           # Registro de usuarios
│   │       ├── dashboard.html          # Panel principal por rol
│   │       ├── reportes.html           # Reportes con gráfica Chart.js
│   │       ├── productos/
│   │       │   ├── lista.html          # Catálogo con botón Comprar
│   │       │   ├── detalle.html        # Ficha completa del producto
│   │       │   └── form.html           # Formulario crear/editar
│   │       ├── proveedores/
│   │       │   ├── lista.html          # Listado de proveedores
│   │       │   ├── detalle.html        # Ficha con facturación total
│   │       │   └── form.html           # Formulario crear proveedor
│   │       └── ventas/
│   │           ├── lista.html          # Historial de ventas/compras
│   │           └── crear.html          # Formulario de compra para clientes
│   └── static/
│       └── core/
│           ├── css/style.css           # Estilos responsive
│           └── js/main.js              # JavaScript general
├── mysite/
│   ├── settings.py                     # Configuración del proyecto
│   ├── urls.py                         # Enrutamiento URL
│   ├── wsgi.py
│   └── asgi.py
├── manage.py
├── db.sqlite3                          # Base de datos SQLite
├── requirements.txt
├── README.md
└── DOCUMENTACION.md
```

---

## Modelo de Datos

### Diagrama ERD

```
User (Django Auth)
  ├── UserRole (1:1)  →  role: admin | cliente | vendedor
  └── Venta (1:N)     →  ventas realizadas por el usuario

Proveedor (1:N) ──────────────────────────────────────────────
  ├── Producto (1:N)  →  productos suministrados
  └── CompraProveedor (1:N)  →  facturas de compra

Producto
  ├── Venta (1:N)             →  ventas de este producto
  └── CompraProveedor (1:N)   →  reposiciones de stock
```

### Descripción de Modelos

#### TimeStampedModel (abstracto)
Clase base heredada por todos los modelos. Añade automáticamente `created_at` y `updated_at` a cada tabla sin crear tabla propia en la BD.

#### UserRole
| Campo | Tipo | Descripción |
|-------|------|-------------|
| user | OneToOneField(User) | Usuario Django asociado |
| role | CharField | admin / cliente / vendedor |

#### Proveedor
| Campo | Tipo | Descripción |
|-------|------|-------------|
| nombre_empresa | CharField | Nombre comercial |
| cif | CharField (unique) | Identificador fiscal |
| telefono | CharField | Teléfono de contacto |
| email | EmailField | Correo electrónico |
| direccion | TextField | Dirección completa |
| ciudad / codigo_postal / pais | CharField | Ubicación |
| persona_contacto | CharField | Interlocutor principal |
| descuento_porcentaje | DecimalField | % descuento negociado |
| iva | DecimalField | % IVA aplicado (default 21%) |
| activo | BooleanField | Estado del proveedor |

Método destacado: `facturacion_total()` — suma el total de todas las compras recibidas usando `aggregate(Sum())` directamente en la BD.

#### Producto
| Campo | Tipo | Descripción |
|-------|------|-------------|
| nombre | CharField | Nombre del producto |
| numero_referencia | CharField (unique) | Código de referencia |
| descripcion | TextField | Descripción detallada |
| categoria | CharField | hardware/software/accesorios/cables/memorias/fuentes/otros |
| proveedor | FK(Proveedor) | Proveedor suministrador |
| precio_compra / precio_venta | DecimalField | Precios |
| stock_actual / stock_minimo | PositiveIntegerField | Control de inventario |
| ubicacion_almacen | CharField | Localización física |
| color / especificaciones | CharField/TextField | Características adicionales |
| imagen | ImageField | Foto del producto |

Métodos destacados:
- `alertar_stock_bajo()` → `True` si `stock_actual <= stock_minimo * 0.9`
- `margen_beneficio()` → `((precio_venta - precio_compra) / precio_compra) * 100`

#### Venta
| Campo | Tipo | Descripción |
|-------|------|-------------|
| numero_venta | CharField (unique) | Generado automáticamente (VEN-YYYYMMDD-HHMMSS) |
| cliente | FK(User) | Cliente que realizó la compra |
| producto | FK(Producto) | Producto adquirido |
| cantidad | PositiveIntegerField | Unidades compradas |
| precio_unitario | DecimalField | Precio en el momento de la venta |
| descuento_aplicado | DecimalField | % descuento |
| estado | CharField | pendiente / completada / cancelada |

Métodos de cálculo: `total_bruto()`, `total_descuento()`, `total_neto()`, `total_con_iva()`

#### CompraProveedor
Igual que Venta pero orientado a compras a proveedores. Incluye `fecha_recepcion` para registrar cuándo llegó el pedido.

---

## Funcionalidades Implementadas

### 1. Autenticación y Control de Acceso

- Login con `AuthenticationForm` personalizado
- Registro con asignación automática de rol `cliente`
- Logout con limpieza de sesión
- `@login_required` en todas las vistas protegidas
- Decorador `requiere_rol(*roles)` en `auth.py` — elimina código duplicado y centraliza el control de acceso

```python
@login_required(login_url='login')
@requiere_rol('admin')
def crear_producto(request):
    ...

@login_required(login_url='login')
@requiere_rol('admin', 'vendedor')
def lista_proveedores(request):
    ...
```

### 2. Dashboard diferenciado por rol

- **Admin**: estadísticas globales (productos, proveedores, stock bajo, ventas totales) + acciones rápidas
- **Cliente**: últimas compras y acceso al catálogo
- **Vendedor**: acceso a inventario y proveedores

### 3. Gestión de Productos

- Listado con búsqueda por nombre/referencia y filtro por categoría
- Alerta visual ⚠️ en tarjetas con stock bajo
- Vista detallada con margen de beneficio (solo admin)
- Crear/editar productos con subida de imagen (solo admin)
- Botón **Comprar** visible para clientes con stock disponible

### 4. Gestión de Proveedores

- Listado con búsqueda por nombre/email
- Ficha de proveedor con datos de contacto, condiciones comerciales y facturación total acumulada
- Listado de productos suministrados con estado de stock
- Crear proveedor (solo admin)

### 5. Sistema de Ventas y Compras

- Flujo completo de compra para clientes:
  1. Cliente pulsa **Comprar** en el catálogo
  2. Selecciona cantidad (validación de stock en tiempo real)
  3. El sistema genera número de venta, aplica precio y descuenta stock automáticamente usando expresiones `F()` para evitar condiciones de carrera
- Historial de ventas filtrable por estado
- Admin y vendedor ven todas las ventas; cliente solo las suyas

### 6. Reportes y Gráficas

- Gráfica de evolución mensual (últimos 12 meses) con Chart.js:
  - Línea morada: unidades vendidas (estado completada)
  - Línea verde: unidades compradas a proveedores (estado recibida)
- Tabla de productos con stock bajo y acceso directo a edición
- Top 10 productos más vendidos
- Ventas agrupadas por categoría

### 7. Alertas de Stock

```python
def alertar_stock_bajo(self):
    umbral = self.stock_minimo * 0.9
    return self.stock_actual <= umbral
```

Cuando el stock cae al 90% del mínimo definido, el producto se marca visualmente en el catálogo y aparece en la sección de alertas del panel de reportes.

---

## Roles y Permisos

| Función | Admin | Cliente | Vendedor |
|---------|:-----:|:-------:|:--------:|
| Ver catálogo | ✅ | ✅ | ✅ |
| Comprar producto | ❌ | ✅ | ❌ |
| Crear producto | ✅ | ❌ | ❌ |
| Editar producto | ✅ | ❌ | ❌ |
| Ver detalle producto | ✅ | ✅ | ✅ |
| Ver proveedores | ✅ | ❌ | ✅ |
| Crear proveedor | ✅ | ❌ | ❌ |
| Ver reportes y gráficas | ✅ | ❌ | ❌ |
| Ver todas las ventas | ✅ | ❌ | ✅ |
| Ver sus propias compras | ✅ | ✅ | N/A |
| Panel administrativo Django | ✅ | ❌ | ❌ |

---

## Lógica de Negocio — Cálculos

### Alerta de stock (corregida)
```python
# Avisa cuando el stock cae por debajo del 90% del mínimo definido
umbral = self.stock_minimo * 0.9
return self.stock_actual <= umbral
```

### Margen de beneficio
```python
return ((self.precio_venta - self.precio_compra) / self.precio_compra) * 100
```

### Facturación con descuentos e IVA
```python
total_bruto = cantidad * precio_unitario
descuento   = total_bruto * (descuento_porcentaje / 100)
total_neto  = total_bruto - descuento
iva         = total_neto * (iva_porcentaje / 100)
total_final = total_neto + iva
```

### Descuento de stock atómico al comprar
```python
# F() hace la resta directamente en BD — evita condiciones de carrera
Producto.objects.filter(pk=producto.pk).update(
    stock_actual=F('stock_actual') - cantidad
)
```

---

## Tests Automatizados

El proyecto incluye **38 tests** organizados en 4 bloques:

```bash
python manage.py test core              # ejecutar todos
python manage.py test core --verbosity=2 # con detalle
```

| Bloque | Tests | Qué cubre |
|--------|-------|-----------|
| TestModeloProducto | 7 | alertar_stock_bajo, margen_beneficio, __str__ |
| TestModeloVenta | 4 | total_bruto, total_descuento, total_neto, total_con_iva |
| TestModeloProveedor | 3 | facturacion_total, __str__ |
| TestVistasPublicas | 6 | login, registro, redirecciones |
| TestVistasProtegidas | 9 | acceso por rol, @login_required |
| TestDecoradorRequiereRol | 4 | requiere_rol con uno y varios roles |
| TestFormularios | 5 | validación de RegisterForm y ProductoForm |

---

## Manual de Instalación

### Requisitos previos
- Python 3.8 o superior
- Git

### Pasos

**1. Clonar el repositorio**
```powershell
git clone https://github.com/ebenval/django_prueba.git
cd django_prueba
```

**2. Crear y activar el entorno virtual**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la ejecución:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**3. Instalar dependencias**
```powershell
pip install -r requirements.txt
```

**4. Aplicar migraciones**
```powershell
python manage.py migrate
```

**5. Poblar la base de datos con datos de prueba**
```powershell
python manage.py poblar_bd
```

Esto crea automáticamente:
- 6 usuarios (1 admin, 2 vendedores, 3 clientes)
- 4 proveedores
- 10 productos con stock variado
- Ventas históricas de los últimos 12 meses
- Compras a proveedores de los últimos 6 meses

Para limpiar y recrear los datos:
```powershell
python manage.py poblar_bd --limpiar
```

**6. Ejecutar el servidor**
```powershell
python manage.py runserver
```

**7. Acceder a la aplicación**
- Aplicación: `http://127.0.0.1:8000`
- Panel admin: `http://127.0.0.1:8000/admin`

### Credenciales de prueba

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| admin | admin123 | Administrador |
| vendedor1 | vendedor123 | Vendedor |
| cliente1 | cliente123 | Cliente |

### Ejecutar tests
```powershell
python manage.py test core --verbosity=2
```

---

## Arquitectura — Decisiones Técnicas

### ¿Por qué Django?
Django incluye ORM, sistema de autenticación, panel de administración y sistema de templates de serie. Permite desarrollar una aplicación completa con menos código que Flask o FastAPI, y tiene convenciones claras que facilitan el mantenimiento.

### ¿Por qué SQLite?
Para desarrollo y proyectos académicos es suficiente, no requiere instalación de servidor separado y el archivo `db.sqlite3` es portable. En producción se migraría a PostgreSQL cambiando únicamente la configuración en `settings.py`.

### ¿Por qué decorador `requiere_rol` en lugar de `if/else` en cada vista?
El bloque de comprobación de rol se repetía en 8 vistas. El decorador centraliza esa lógica en `auth.py` — si cambia la lógica de permisos, se modifica en un único lugar.

### ¿Por qué `F()` al descontar stock?
```python
Producto.objects.filter(pk=pk).update(stock_actual=F('stock_actual') - cantidad)
```
Si dos clientes compran el mismo producto simultáneamente, sin `F()` ambos leerían el mismo stock y lo restarían por separado, resultando en stock incorrecto. `F()` delega la operación a la BD, que la ejecuta de forma atómica.

---

## Evolutivos del Proyecto

Mejoras identificadas para futuras versiones:

1. **Segunda gráfica comparativa** — ingresos por ventas vs costes de compras en euros
2. **Gráfica para clientes** — evolución de sus compras por mes en el dashboard
3. **Securizar SECRET_KEY** — mover a `.env` con `python-dotenv` (instrucciones en sección Variables de Entorno)
4. **Exportación CSV** — botón para descargar ventas o productos en formato Excel/CSV
5. **Paginación** — en listas con muchos registros usando `Paginator` de Django
6. **Confirmación de borrado** — modal JavaScript antes de eliminar registros críticos
7. **Facturación PDF** — generar facturas descargables con `reportlab` o `weasyprint`
8. **Notificaciones por email** — alertas automáticas cuando el stock baje del umbral
9. **API REST** — endpoints con Django REST Framework para integración con apps móviles
10. **2FA** — autenticación de dos factores con `django-otp`

---

## Conclusiones

El proyecto implementa una aplicación web de gestión empresarial completa que cumple y supera los requisitos mínimos del enunciado. Los aspectos más destacados son:

- Arquitectura limpia con separación clara de responsabilidades (models/views/forms/templates)
- Sistema de control de acceso robusto con decorador reutilizable
- Tests automatizados que garantizan el correcto funcionamiento de la lógica de negocio
- Datos de prueba realistas generados automáticamente mediante management command
- Interfaz responsive y navegación dinámica adaptada al rol del usuario

El mayor aprendizaje del proyecto ha sido la importancia de los patrones de diseño en Django — la herencia de modelos, los decoradores de Python y las expresiones `F()` del ORM son herramientas que resuelven problemas reales de forma elegante y eficiente.

---

**Versión**: 2.0
**Última Actualización**: Abril 2026
