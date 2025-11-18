# Proyecto Django - mysite

Proyecto base con Django y una app mínima `core`.

Descripción
-----------
Este repositorio contiene un proyecto Django de ejemplo llamado `mysite` y una aplicación local `core`.
Está preparado para desarrollo local con SQLite y un entorno virtual.

Requisitos
----------
- Python 3.8 o superior
- Git

Archivos clave
--------------
- `manage.py` — script de administración de Django
- `mysite/` — configuración del proyecto (settings, urls, wsgi/asgi)
- `core/` — app Django de ejemplo
- `requirements.txt` — dependencias del proyecto

Instalación rápida (PowerShell)
-------------------------------
1) Abrir PowerShell en la carpeta del proyecto:

```powershell
cd C:\Users\ebenv\Desktop\django_prueba
```

2) Crear y activar el entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3) (Opcional) Si PowerShell bloquea la activación por políticas, permitir ejecución para el usuario:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

4) Instalar dependencias:

```powershell
pip install -r requirements.txt
```

Uso (comandos frecuentes)
-------------------------
- Ejecutar servidor de desarrollo:

```powershell
python manage.py runserver
# abrir http://127.0.0.1:8000
```

- Aplicar migraciones:

```powershell
python manage.py migrate
```

- Crear superusuario (para acceder al admin):

```powershell
python manage.py createsuperuser
```

- Ejecutar tests:

```powershell
python manage.py test
```

Variables de entorno
--------------------
Si necesitas variables sensibles (clave secreta, configuración externa), crea un archivo `.env` y usa `python-dotenv` o configura variables en el entorno del sistema.

Ejemplo `.env` (no lo incluyas en el repo):

```
SECRET_KEY=changeme
DEBUG=True
```

VS Code — tareas útiles
----------------------
Se ha añadido un archivo `/.vscode/tasks.json` con tareas para:
- Instalar dependencias (`pip install -r requirements.txt`)
- Ejecutar el servidor de desarrollo (`python manage.py runserver 0.0.0.0:8000`)

Recomendaciones
---------------
- Extensión VS Code recomendada: `ms-python.python`
- Usa un entorno virtual por proyecto (`.venv`) y añade `.venv/` a `.gitignore` (ya incluido).

Despliegue
---------
Este proyecto está pensado para desarrollo local. Para producción usa un servidor WSGI/ASGI adecuado (Gunicorn, Daphne, etc.), configura `ALLOWED_HOSTS`, y usa variables de entorno para secretos.

Contribuir
----------
1. Haz un fork y crea una rama nueva para tu feature/fix
2. Crea un commit claro y abre un pull request

Licencia
--------
Añade aquí la licencia que prefieras (por ejemplo MIT) o elimina esta sección si aún no decides.

Contacto
-------
Si necesitas ayuda con la configuración, describe el problema en un issue en GitHub o contáctame por el canal que prefieras.

---

Fecha: 2025-11-05
