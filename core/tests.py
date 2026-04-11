"""
Tests de la aplicación core.

¿QUÉ ES UN TEST EN DJANGO?
============================
Un test es código que comprueba automáticamente que tu aplicación
funciona como esperas. En lugar de probar manualmente en el navegador,
escribes código que hace la prueba por ti.

Ventaja clave: si más adelante cambias algo y rompes algo sin darte cuenta,
los tests lo detectan al instante.

CÓMO EJECUTAR LOS TESTS:
    python manage.py test core                  → todos los tests de la app
    python manage.py test core.tests.TestModelos → solo una clase
    python manage.py test core.tests.TestModelos.test_alerta_stock_bajo → solo uno

ESTRUCTURA:
    Cada clase agrupa tests relacionados y hereda de TestCase.
    Cada método que empiece por test_ es un test individual.
    setUp() se ejecuta ANTES de cada test para preparar datos limpios.

    Django crea una base de datos temporal solo para tests y la destruye
    al terminar. Nunca toca tu base de datos real (db.sqlite3).
"""

from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from core.models import UserRole, Proveedor, Producto, Venta, CompraProveedor
from core.forms import LoginForm, RegisterForm, ProductoForm


# ===========================================================================
# UTILIDADES COMPARTIDAS
# Funciones auxiliares para no repetir código de creación de objetos
# ===========================================================================

def crear_usuario(username='testuser', rol='cliente', password='pass1234Test'):
    """
    Crea un usuario con su rol asociado.
    Función auxiliar reutilizada en múltiples clases de tests.
    """
    user = User.objects.create_user(username=username, password=password)
    UserRole.objects.create(user=user, role=rol)
    return user


def crear_proveedor(cif='B12345678'):
    """Crea un proveedor de prueba con datos mínimos válidos."""
    return Proveedor.objects.create(
        nombre_empresa='Proveedor Test S.L.',
        cif=cif,
        telefono='912345678',
        email='test@proveedor.com',
        direccion='Calle Test, 1',
        ciudad='Madrid',
        codigo_postal='28001',
        pais='España',
        persona_contacto='Juan Test',
        descuento_porcentaje=Decimal('5.00'),
        iva=Decimal('21.00'),
    )


def crear_producto(proveedor, referencia='REF-001', stock_actual=50, stock_minimo=10):
    """Crea un producto de prueba."""
    return Producto.objects.create(
        nombre='Producto Test',
        numero_referencia=referencia,
        descripcion='Descripción de prueba',
        categoria='hardware',
        proveedor=proveedor,
        precio_compra=Decimal('50.00'),
        precio_venta=Decimal('80.00'),
        stock_actual=stock_actual,
        stock_minimo=stock_minimo,
    )


# ===========================================================================
# BLOQUE 1 — TESTS DE MODELOS
# Comprueban que la lógica de negocio en models.py es correcta.
# Son los más importantes porque son la base de toda la aplicación.
# ===========================================================================

class TestModeloProducto(TestCase):
    """
    Tests para el modelo Producto.

    setUp() se ejecuta antes de CADA test de esta clase.
    Crea datos frescos para que los tests sean independientes entre sí.
    Si un test modifica datos, no afecta al siguiente.
    """

    def setUp(self):
        """Prepara datos comunes para todos los tests de esta clase."""
        self.proveedor = crear_proveedor()

    def test_alerta_stock_bajo_activa_al_90_porciento(self):
        """
        CASO: stock_actual <= 90% del stock_minimo → debe alertar.

        Con stock_minimo=10, el umbral es 10 * 0.9 = 9.
        Si stock_actual=9, debería devolver True (alerta activa).

        assertEqual/assertTrue/assertFalse son los métodos de comprobación.
        Si la condición no se cumple, el test falla y Django muestra el mensaje.
        """
        producto = crear_producto(self.proveedor, stock_actual=9, stock_minimo=10)
        self.assertTrue(
            producto.alertar_stock_bajo(),
            "Debería alertar cuando stock_actual (9) <= 90% de stock_minimo (10)"
        )

    def test_alerta_stock_bajo_no_activa_con_stock_suficiente(self):
        """CASO: stock_actual > 90% del stock_minimo → NO debe alertar."""
        producto = crear_producto(self.proveedor, stock_actual=10, stock_minimo=10)
        self.assertFalse(
            producto.alertar_stock_bajo(),
            "NO debería alertar cuando stock_actual (10) > 90% de stock_minimo (10)"
        )

    def test_alerta_stock_bajo_con_stock_cero(self):
        """CASO: stock_actual=0 → siempre debe alertar."""
        producto = crear_producto(self.proveedor, stock_actual=0, stock_minimo=10)
        self.assertTrue(producto.alertar_stock_bajo())

    def test_alerta_stock_caso_limite_exactamente_umbral(self):
        """
        CASO LÍMITE: stock_actual exactamente igual al umbral.
        Con stock_minimo=20, umbral = 20 * 0.9 = 18.
        Si stock_actual=18 → debe alertar (<=).
        Si stock_actual=19 → NO debe alertar (>).
        """
        producto_en_umbral = crear_producto(
            self.proveedor, referencia='REF-LIM-1',
            stock_actual=18, stock_minimo=20
        )
        producto_sobre_umbral = crear_producto(
            self.proveedor, referencia='REF-LIM-2',
            stock_actual=19, stock_minimo=20
        )
        self.assertTrue(producto_en_umbral.alertar_stock_bajo())
        self.assertFalse(producto_sobre_umbral.alertar_stock_bajo())

    def test_margen_beneficio_calculo_correcto(self):
        """
        Comprueba que margen_beneficio() calcula bien el porcentaje.
        Fórmula: ((precio_venta - precio_compra) / precio_compra) * 100
        Con compra=50, venta=80 → margen = (30/50)*100 = 60%
        """
        producto = crear_producto(self.proveedor)
        margen = producto.margen_beneficio()
        self.assertAlmostEqual(
            float(margen), 60.0, places=1,
            msg="El margen debería ser 60% con compra=50€ y venta=80€"
        )

    def test_margen_beneficio_precio_compra_cero(self):
        """
        CASO EXTREMO: precio_compra=0 → debe devolver 0, no dividir por cero.
        Sin este test, un precio_compra=0 lanzaría ZeroDivisionError.
        """
        producto = crear_producto(self.proveedor)
        producto.precio_compra = Decimal('0')
        self.assertEqual(producto.margen_beneficio(), 0)

    def test_str_devuelve_nombre_y_referencia(self):
        """
        __str__() debe devolver "nombre (referencia)".
        Esto es lo que aparece en el panel de admin y en los selects.
        """
        producto = crear_producto(self.proveedor, referencia='REF-TEST')
        self.assertIn('Producto Test', str(producto))
        self.assertIn('REF-TEST', str(producto))


class TestModeloVenta(TestCase):
    """Tests para los métodos de cálculo del modelo Venta."""

    def setUp(self):
        self.proveedor = crear_proveedor()
        self.producto = crear_producto(self.proveedor)
        self.cliente = crear_usuario(username='cliente_venta', rol='cliente')

        # Creamos una venta base para los tests de cálculo
        self.venta = Venta.objects.create(
            numero_venta='VEN-TEST-001',
            cliente=self.cliente,
            producto=self.producto,
            cantidad=3,
            precio_unitario=Decimal('80.00'),
            descuento_aplicado=Decimal('10.00'),  # 10% descuento
            estado='completada',
        )

    def test_total_bruto(self):
        """3 uds × 80€ = 240€"""
        self.assertEqual(self.venta.total_bruto(), Decimal('240.00'))

    def test_total_descuento(self):
        """10% de 240€ = 24€"""
        self.assertEqual(self.venta.total_descuento(), Decimal('24.00'))

    def test_total_neto(self):
        """240€ - 24€ = 216€"""
        self.assertEqual(self.venta.total_neto(), Decimal('216.00'))

    def test_total_con_iva(self):
        """
        IVA del proveedor es 21%.
        216€ + 21% = 216 + 45.36 = 261.36€
        """
        esperado = Decimal('261.36')
        self.assertAlmostEqual(
            float(self.venta.total_con_iva()), float(esperado), places=2
        )


class TestModeloProveedor(TestCase):
    """Tests para el modelo Proveedor."""

    def setUp(self):
        self.proveedor = crear_proveedor()

    def test_str_devuelve_nombre_empresa(self):
        self.assertEqual(str(self.proveedor), 'Proveedor Test S.L.')

    def test_facturacion_total_sin_compras(self):
        """Sin compras, la facturación debe ser 0."""
        self.assertEqual(self.proveedor.facturacion_total(), 0)

    def test_facturacion_total_con_compras(self):
        """
        Con una compra recibida de 5 uds × 50€ = 250€,
        la facturación total debe ser 250€.
        """
        producto = crear_producto(self.proveedor)
        CompraProveedor.objects.create(
            numero_factura='FAC-TEST-001',
            proveedor=self.proveedor,
            producto=producto,
            cantidad=5,
            precio_unitario=Decimal('50.00'),
            estado='recibida',
        )
        self.assertEqual(self.proveedor.facturacion_total(), Decimal('50.00'))


# ===========================================================================
# BLOQUE 2 — TESTS DE VISTAS
# Comprueban que las URLs responden correctamente y redirigen bien.
# Usamos self.client, que simula un navegador sin abrir Chrome.
# ===========================================================================

class TestVistasPublicas(TestCase):
    """
    Tests para vistas que no requieren login.

    self.client es una instancia de django.test.Client que simula
    peticiones HTTP (GET, POST) sin necesitar un navegador real.

    reverse('nombre_url') devuelve la URL a partir del nombre definido
    en urls.py. Mejor que escribir '/login/' directamente, porque si
    cambias la URL en urls.py, el test sigue funcionando.
    """

    def test_index_redirige_a_login_si_no_autenticado(self):
        """
        GET / sin sesión → debe redirigir a /login/
        assertRedirects comprueba código 302 y la URL destino.
        """
        response = self.client.get(reverse('index'))
        self.assertRedirects(response, reverse('login'))

    def test_login_page_carga_correctamente(self):
        """
        GET /login/ → debe devolver código 200 (OK).
        assertEqual(200) es la forma más directa de comprobar que la página carga.
        """
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_usa_template_correcto(self):
        """
        assertTemplateUsed comprueba qué template renderizó Django.
        Útil para detectar si una vista usa accidentalmente el template equivocado.
        """
        response = self.client.get(reverse('login'))
        self.assertTemplateUsed(response, 'core/login.html')

    def test_register_page_carga_correctamente(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_login_con_credenciales_correctas(self):
        """
        POST /login/ con datos válidos → debe redirigir al dashboard.
        self.client.post() simula enviar un formulario.
        """
        crear_usuario(username='user_login', password='pass1234Test', rol='cliente')
        response = self.client.post(reverse('login'), {
            'username': 'user_login',
            'password': 'pass1234Test',
        })
        self.assertRedirects(response, reverse('dashboard'))

    def test_login_con_credenciales_incorrectas(self):
        """
        POST /login/ con contraseña incorrecta → debe quedarse en login (200).
        NO debe redirigir al dashboard.
        """
        crear_usuario(username='user_bad', password='pass1234Test', rol='cliente')
        response = self.client.post(reverse('login'), {
            'username': 'user_bad',
            'password': 'contraseña_incorrecta',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/login.html')


class TestVistasProtegidas(TestCase):
    """
    Tests para vistas que requieren login o roles específicos.

    self.client.login() simula el inicio de sesión.
    Devuelve True si el login fue exitoso, False si falló.
    """

    def setUp(self):
        self.admin   = crear_usuario(username='admin_test',    rol='admin',    password='admin1234Test')
        self.cliente = crear_usuario(username='cliente_test',  rol='cliente',  password='cliente1234Test')
        self.vendedor= crear_usuario(username='vendedor_test', rol='vendedor', password='vendedor1234Test')
        self.proveedor = crear_proveedor()
        self.producto  = crear_producto(self.proveedor)

    def test_dashboard_requiere_login(self):
        """
        Sin sesión, /dashboard/ debe redirigir a /login/.
        El ?next=/dashboard/ es el comportamiento estándar de @login_required.
        """
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")

    def test_dashboard_accesible_para_admin(self):
        """Admin logueado puede acceder al dashboard."""
        self.client.login(username='admin_test', password='admin1234Test')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_accesible_para_cliente(self):
        """Cliente logueado puede acceder al dashboard."""
        self.client.login(username='cliente_test', password='cliente1234Test')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_lista_productos_accesible_para_todos(self):
        """Todos los roles pueden ver el catálogo."""
        for username, password in [
            ('admin_test', 'admin1234Test'),
            ('cliente_test', 'cliente1234Test'),
            ('vendedor_test', 'vendedor1234Test'),
        ]:
            self.client.login(username=username, password=password)
            response = self.client.get(reverse('lista_productos'))
            self.assertEqual(
                response.status_code, 200,
                f"El rol {username} debería poder ver la lista de productos"
            )

    def test_crear_producto_solo_admin(self):
        """
        Solo el admin puede acceder a crear producto.
        Cliente y vendedor deben ser redirigidos al dashboard.
        """
        # Admin → OK
        self.client.login(username='admin_test', password='admin1234Test')
        response = self.client.get(reverse('crear_producto'))
        self.assertEqual(response.status_code, 200)

        # Cliente → redirigido
        self.client.login(username='cliente_test', password='cliente1234Test')
        response = self.client.get(reverse('crear_producto'))
        self.assertRedirects(response, reverse('dashboard'))

        # Vendedor → redirigido
        self.client.login(username='vendedor_test', password='vendedor1234Test')
        response = self.client.get(reverse('crear_producto'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_reportes_solo_admin(self):
        """Solo admin puede ver reportes. Cliente es redirigido."""
        self.client.login(username='admin_test', password='admin1234Test')
        response = self.client.get(reverse('reportes'))
        self.assertEqual(response.status_code, 200)

        self.client.login(username='cliente_test', password='cliente1234Test')
        response = self.client.get(reverse('reportes'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_proveedores_no_accesibles_para_cliente(self):
        """Cliente no puede ver proveedores."""
        self.client.login(username='cliente_test', password='cliente1234Test')
        response = self.client.get(reverse('lista_proveedores'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_proveedores_accesibles_para_vendedor(self):
        """Vendedor sí puede ver proveedores."""
        self.client.login(username='vendedor_test', password='vendedor1234Test')
        response = self.client.get(reverse('lista_proveedores'))
        self.assertEqual(response.status_code, 200)

    def test_logout_cierra_sesion_y_redirige(self):
        """Logout debe cerrar la sesión y redirigir a login."""
        self.client.login(username='admin_test', password='admin1234Test')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

        # Tras el logout, dashboard debe pedir login de nuevo
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('dashboard')}"
        )


# ===========================================================================
# BLOQUE 3 — TESTS DEL DECORADOR requiere_rol
# Comprueban que auth.py funciona correctamente.
# ===========================================================================

class TestDecoradorRequiereRol(TestCase):
    """
    Tests para el decorador requiere_rol de auth.py.
    Comprobamos que bloquea correctamente según el rol.
    """

    def setUp(self):
        self.admin   = crear_usuario(username='dec_admin',    rol='admin',    password='admin1234Test')
        self.cliente = crear_usuario(username='dec_cliente',  rol='cliente',  password='cliente1234Test')
        self.vendedor= crear_usuario(username='dec_vendedor', rol='vendedor', password='vendedor1234Test')
        self.proveedor = crear_proveedor()

    def test_admin_puede_crear_proveedor(self):
        """Admin tiene acceso a vistas protegidas con @requiere_rol('admin')."""
        self.client.login(username='dec_admin', password='admin1234Test')
        response = self.client.get(reverse('crear_proveedor'))
        self.assertEqual(response.status_code, 200)

    def test_cliente_no_puede_crear_proveedor(self):
        """Cliente bloqueado por @requiere_rol('admin')."""
        self.client.login(username='dec_cliente', password='cliente1234Test')
        response = self.client.get(reverse('crear_proveedor'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_vendedor_no_puede_crear_proveedor(self):
        """Vendedor bloqueado por @requiere_rol('admin')."""
        self.client.login(username='dec_vendedor', password='vendedor1234Test')
        response = self.client.get(reverse('crear_proveedor'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_vendedor_puede_ver_lista_proveedores(self):
        """
        Vendedor sí puede acceder a @requiere_rol('admin', 'vendedor').
        Comprobamos que múltiples roles funcionan correctamente.
        """
        self.client.login(username='dec_vendedor', password='vendedor1234Test')
        response = self.client.get(reverse('lista_proveedores'))
        self.assertEqual(response.status_code, 200)


# ===========================================================================
# BLOQUE 4 — TESTS DE FORMULARIOS
# Comprueban que los formularios validan correctamente los datos.
# ===========================================================================

class TestFormularios(TestCase):
    """
    Tests de validación de formularios.

    Un formulario válido debe pasar is_valid() → True.
    Un formulario con datos incorrectos debe fallar → False.

    Los tests de formularios son más rápidos que los de vistas
    porque no necesitan hacer peticiones HTTP.
    """

    def test_register_form_valido(self):
        """Datos correctos → formulario válido."""
        form = RegisterForm(data={
            'username': 'nuevo_usuario',
            'email': 'nuevo@test.com',
            'password1': 'ContraseñaSegura123!',
            'password2': 'ContraseñaSegura123!',
        })
        self.assertTrue(form.is_valid(), f"Errores: {form.errors}")

    def test_register_form_passwords_no_coinciden(self):
        """Contraseñas distintas → formulario inválido."""
        form = RegisterForm(data={
            'username': 'otro_usuario',
            'email': 'otro@test.com',
            'password1': 'ContraseñaSegura123!',
            'password2': 'ContraseñaDiferente456!',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_register_form_username_vacio(self):
        """Username vacío → formulario inválido."""
        form = RegisterForm(data={
            'username': '',
            'email': 'test@test.com',
            'password1': 'ContraseñaSegura123!',
            'password2': 'ContraseñaSegura123!',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_producto_form_valido(self):
        """Formulario de producto con todos los campos requeridos → válido."""
        proveedor = crear_proveedor()
        form = ProductoForm(data={
            'nombre': 'Producto Formulario Test',
            'numero_referencia': 'REF-FORM-001',
            'descripcion': 'Descripción de prueba del formulario',
            'categoria': 'hardware',
            'proveedor': proveedor.pk,
            'precio_compra': '40.00',
            'precio_venta': '65.00',
            'stock_actual': '25',
            'stock_minimo': '10',
            'ubicacion_almacen': 'Estantería A-01',
            'color': 'Negro',
            'especificaciones': '',
            'activo': True,
        })
        self.assertTrue(form.is_valid(), f"Errores del formulario: {form.errors}")

    def test_producto_form_precio_venta_requerido(self):
        """Sin precio de venta → formulario inválido."""
        proveedor = crear_proveedor()
        form = ProductoForm(data={
            'nombre': 'Producto sin precio',
            'numero_referencia': 'REF-FORM-002',
            'descripcion': 'Test',
            'categoria': 'hardware',
            'proveedor': proveedor.pk,
            'precio_compra': '40.00',
            'precio_venta': '',      # ← campo vacío
            'stock_actual': '10',
            'stock_minimo': '5',
            'activo': True,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('precio_venta', form.errors)
