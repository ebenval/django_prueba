# SuministrosIT — Sistema de Gestión de Suministros Informáticos

Aplicación web desarrollada con **Django (Python)** para la gestión integral de una empresa de suministros informáticos. Permite administrar productos, proveedores, ventas y clientes con control de acceso por roles.

---

## Funcionalidades principales

- Gestión de inventario con alertas automáticas de stock bajo (90% del mínimo)
- Catálogo de productos con búsqueda, filtros y compra para clientes
- Administración completa de proveedores con facturación e IVA
- Sistema de ventas con descuento de stock atómico
- Reportes con gráfica de evolución mensual (Chart.js)
- Control de acceso con 3 roles: Administrador, Vendedor y Cliente
- Panel de administración Django integrado
- 38 tests automatizados

---

## Requisitos previos

### Obligatorio instalar manualmente

| Requisito | Versión mínima | Descarga |
|-----------|---------------|---------|
| Python | 3.8+ | https://www.python.org/downloads/ |
| Git | cualquiera | https://git-scm.com/downloads |

> `pip` viene incluido con Python 3.4+. No necesita instalación separada.

### Se instalan automáticamente con `pip install -r requirements.txt`

| Paquete | Versión | Para qué sirve |
|---------|---------|---------------|
| Django | 4.2+ | Framework web (ORM, Auth, Admin, Templates) |
| Pillow | 10.0+ | Procesamiento de imágenes de productos |
| python-dotenv | cualquiera | Carga de variables de entorno desde .env |

### No requiere instalación adicional

| Tecnología | Motivo |
|-----------|--------|
| SQLite | Incluido en Python — no necesita servidor de base de datos |
| Chart.js | Se carga desde CDN en el navegador al abrir reportes |

> Chart.js requiere **conexión a Internet** al abrir la página de reportes.

### Solo Windows

PowerShell está incluido en Windows 10 y 11. Si la activación del entorno virtual está bloqueada:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Instalación — Opción A: descargando desde GitHub

> Usa esta opción si tienes Git instalado y cuenta en GitHub.

**Paso 1 — Verificar que Python está instalado correctamente**

```powershell
python --version
pip --version
```

Ambos deben devolver un número de versión. Si `python` no se reconoce, añade Python al PATH durante la instalación marcando la casilla "Add Python to PATH".

**Paso 2 — Clonar el repositorio**

```powershell
git clone https://github.com/ebenval/django_prueba.git
cd django_prueba
```

**Paso 3 — Crear el entorno virtual**

```powershell
python -m venv .venv
```

> Un entorno virtual es una carpeta aislada donde se instalan las dependencias del proyecto sin afectar al resto del sistema.

**Paso 4 — Activar el entorno virtual**

```powershell
.\.venv\Scripts\Activate.ps1
```

Sabrás que está activo porque el prompt cambia a `(.venv) PS C:\...`

Si da error de permisos:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Y vuelve a ejecutar el paso 4.

**Paso 5 — Instalar dependencias**

```powershell
pip install -r requirements.txt
```

Esto instala Django, Pillow y python-dotenv automáticamente. Puede tardar un par de minutos.

**Paso 6 — Configurar carpeta de imágenes**

Crea la carpeta donde se guardarán las imágenes de productos:

```powershell
mkdir media
mkdir media\productos
```

**Paso 7 — Aplicar migraciones**

Crea la base de datos SQLite con todas las tablas:

```powershell
python manage.py migrate
```

Debe terminar con `OK` en todas las líneas.

**Paso 8 — Poblar la base de datos con datos de prueba**

```powershell
python manage.py poblar_bd
```

Crea 6 usuarios, 4 proveedores, 10 productos y ventas históricas de 12 meses. Para limpiar y recrear desde cero:

```powershell
python manage.py poblar_bd --limpiar
```

**Paso 9 — Verificar que los tests pasan**

```powershell
python manage.py test core --verbosity=2
```

Resultado esperado: `Ran 38 tests ... OK`

**Paso 10 — Arrancar el servidor**

```powershell
python manage.py runserver
```

Abre el navegador en `http://127.0.0.1:8000`

---

## Instalación — Opción B: descargando el ZIP (sin GitHub)

> Usa esta opción si no tienes Git o no quieres usar GitHub.

**Paso 1 — Verificar que Python está instalado**

```powershell
python --version
pip --version
```

Si no están instalados, descarga Python desde https://www.python.org/downloads/ marcando la casilla **"Add Python to PATH"** durante la instalación.

**Paso 2 — Descargar el proyecto como ZIP**

Entra en https://github.com/ebenval/django_prueba, pulsa el botón verde **"Code"** y selecciona **"Download ZIP"**. Extrae el contenido en una carpeta de tu equipo, por ejemplo `C:\Proyectos\django_prueba`.

**Paso 3 — Abrir PowerShell en la carpeta del proyecto**

Navega hasta la carpeta donde extrajiste el ZIP:

```powershell
cd C:\Proyectos\django_prueba
```

O más fácil: abre la carpeta en el Explorador de Windows, haz clic derecho en un espacio vacío y selecciona "Abrir en Terminal".

**Paso 4 — Crear el entorno virtual**

```powershell
python -m venv .venv
```

**Paso 5 — Activar el entorno virtual**

```powershell
.\.venv\Scripts\Activate.ps1
```

El prompt cambia a `(.venv) PS C:\...` cuando está activo.

Si da error de permisos:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Y vuelve a ejecutar el paso 5.

**Paso 6 — Instalar dependencias**

```powershell
pip install -r requirements.txt
```

**Paso 7 — Configurar carpeta de imágenes**

```powershell
mkdir media
mkdir media\productos
```

**Paso 8 — Aplicar migraciones**

```powershell
python manage.py migrate
```

**Paso 9 — Poblar la base de datos con datos de prueba**

```powershell
python manage.py poblar_bd
```

**Paso 10 — Verificar que los tests pasan**

```powershell
python manage.py test core --verbosity=2
```

Resultado esperado: `Ran 38 tests ... OK`

**Paso 11 — Arrancar el servidor**

```powershell
python manage.py runserver
```

Abre el navegador en `http://127.0.0.1:8000`

---

## Credenciales de prueba

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| `admin` | `admin123` | Administrador — acceso total |
| `vendedor1` | `vendedor123` | Vendedor — productos y proveedores |
| `cliente1` | `cliente123` | Cliente — catálogo y compras |

---

## URLs de la aplicación

| URL | Descripción |
|-----|-------------|
| `http://127.0.0.1:8000` | Aplicación principal |
| `http://127.0.0.1:8000/admin` | Panel de administración Django |

---

## Problemas frecuentes

**`python` no se reconoce como comando**
Python no está en el PATH. Reinstala Python marcando "Add Python to PATH" o añádelo manualmente en las variables de entorno de Windows.

**Error al activar el entorno virtual**
Ejecuta `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` y vuelve a intentarlo.

**`No such table` al arrancar**
No se han aplicado las migraciones. Ejecuta `python manage.py migrate`.

**Las gráficas no aparecen en reportes**
Chart.js se carga desde Internet. Verifica que tienes conexión a Internet o que tu red no bloquea `cdn.jsdelivr.net`.

**Las imágenes de productos no se guardan**
Verifica que existe la carpeta `media/productos/` en la raíz del proyecto. Si no existe, créala con `mkdir media\productos`.

**`ModuleNotFoundError: No module named 'django'`**
El entorno virtual no está activo. Ejecuta `.\.venv\Scripts\Activate.ps1` antes de cualquier comando.

---

## Comandos útiles

```powershell
# Arrancar el servidor
python manage.py runserver

# Aplicar migraciones
python manage.py migrate

# Poblar base de datos
python manage.py poblar_bd

# Limpiar y repoblar
python manage.py poblar_bd --limpiar

# Ejecutar tests
python manage.py test core --verbosity=2

# Crear superusuario manualmente
python manage.py createsuperuser
```

---

## Variables de entorno (opcional)

Crea un archivo `.env` en la raíz del proyecto para no exponer la clave secreta:

```
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## Estructura del proyecto

```
django_prueba/
├── core/                   # App principal
│   ├── models.py           # 5 modelos de datos
│   ├── views.py            # Lógica de vistas
│   ├── forms.py            # Formularios con validación
│   ├── auth.py             # Decorador requiere_rol
│   ├── admin.py            # Panel administrativo
│   ├── tests.py            # 38 tests automatizados
│   ├── management/
│   │   └── commands/
│   │       └── poblar_bd.py
│   ├── templates/
│   └── static/
├── mysite/
│   ├── settings.py
│   └── urls.py
├── media/                  # Imágenes subidas (crear manualmente)
├── requirements.txt
├── README.md
└── DOCUMENTACION.md
```

---

## Documentación completa

Consulta `DOCUMENTACION.md` para información detallada sobre arquitectura, modelo de datos, requisitos funcionales y evolutivos.

---

**Versión**: 2.0 | **Actualización**: Abril 2026
