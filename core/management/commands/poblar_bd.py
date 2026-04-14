

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import datetime
import random

from core.models import UserRole, Proveedor, Producto, Venta, CompraProveedor


class Command(BaseCommand):
    """
    Comando para poblar la base de datos con datos de prueba.

    self.stdout.write() es la forma correcta de imprimir en management commands.
    Equivale a print() pero usa el sistema de salida de Django,
    lo que permite redirigir la salida y colorear mensajes.

    self.style.SUCCESS()  → texto verde
    self.style.WARNING()  → texto amarillo
    self.style.ERROR()    → texto rojo
    """

    # Descripción que aparece al ejecutar: python manage.py help poblar_bd
    help = 'Pobla la base de datos con datos de prueba para la empresa de suministros informáticos.'

    def add_arguments(self, parser):
        """
        add_arguments permite definir opciones para el comando.

        --limpiar es un argumento opcional de tipo booleano (flag).
        Si lo incluyes al ejecutar el comando, su valor será True.
        Si no lo incluyes, será False (action='store_true').

        Uso:
            python manage.py poblar_bd             → solo crea datos
            python manage.py poblar_bd --limpiar   → borra y recrea todo
        """
        parser.add_argument(
            '--limpiar',
            action='store_true',
            help='Elimina todos los datos existentes antes de crear los nuevos.',
        )

    def handle(self, *args, **options):
        """
        Punto de entrada del comando. Django llama a este método al ejecutarlo.

        options es un diccionario con los argumentos parseados.
        options['limpiar'] será True o False según lo que pasaste.
        """

        # Si se pasó --limpiar, borramos todo primero
        if options['limpiar']:
            self._limpiar_datos()

        self.stdout.write('\n' + '='*50)
        self.stdout.write('  Poblando base de datos de SuministrosIT')
        self.stdout.write('='*50 + '\n')

        # Ejecutamos cada sección en orden (respetando las FK)
        usuarios    = self._crear_usuarios()
        proveedores = self._crear_proveedores()
        productos   = self._crear_productos(proveedores)
        ventas      = self._crear_ventas(usuarios, productos)
        self._crear_compras(proveedores, productos)

        self.stdout.write('\n' + self.style.SUCCESS('✓ Base de datos poblada correctamente.'))
        self.stdout.write(self.style.SUCCESS(
            f'  · {len(usuarios)} usuarios · {len(proveedores)} proveedores · '
            f'{len(productos)} productos · {len(ventas)} ventas\n'
        ))
        self.stdout.write('Accede con:')
        self.stdout.write('  Admin    → usuario: admin       contraseña: admin123')
        self.stdout.write('  Vendedor → usuario: vendedor1   contraseña: vendedor123')
        self.stdout.write('  Cliente  → usuario: cliente1    contraseña: cliente123\n')

    # ------------------------------------------------------------------
    # MÉTODOS PRIVADOS — cada uno crea una parte de los datos
    # El prefijo _ indica que son de uso interno de esta clase
    # ------------------------------------------------------------------

    def _limpiar_datos(self):
        """Elimina todos los datos creados por este comando."""
        self.stdout.write(self.style.WARNING('⚠  Eliminando datos existentes...'))

        # El orden importa: primero eliminamos los que tienen FK hacia otros
        # para no violar restricciones de integridad referencial.
        CompraProveedor.objects.all().delete()
        Venta.objects.all().delete()
        Producto.objects.all().delete()
        Proveedor.objects.all().delete()
        UserRole.objects.all().delete()
        # Eliminamos usuarios excepto el superusuario (is_superuser=True)
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.WARNING('   Datos eliminados.\n'))

    def _crear_usuarios(self):
        """
        Crea usuarios de prueba para cada rol.

        get_or_create() es muy útil aquí:
        - Si el usuario YA existe (de una ejecución anterior), lo devuelve sin error.
        - Si NO existe, lo crea.
        - Devuelve una tupla: (objeto, created)
          created es True si se acaba de crear, False si ya existía.

        Esto hace que el comando sea IDEMPOTENTE: puedes ejecutarlo
        varias veces sin duplicar datos ni romper nada.
        """
        self.stdout.write('👤 Creando usuarios...')
        usuarios_creados = []

        datos_usuarios = [
            {
                'username': 'admin',
                'email': 'admin@suministrosit.com',
                'password': 'admin123',
                'first_name': 'Carlos',
                'last_name': 'García',
                'rol': 'admin',
                'is_staff': True,
                'is_superuser': True,
            },
            {
                'username': 'vendedor1',
                'email': 'vendedor1@suministrosit.com',
                'password': 'vendedor123',
                'first_name': 'Laura',
                'last_name': 'Martínez',
                'rol': 'vendedor',
                'is_staff': False,
            },
            {
                'username': 'vendedor2',
                'email': 'vendedor2@suministrosit.com',
                'password': 'vendedor123',
                'first_name': 'Pedro',
                'last_name': 'Sánchez',
                'rol': 'vendedor',
                'is_staff': False,
            },
            {
                'username': 'cliente1',
                'email': 'cliente1@email.com',
                'password': 'cliente123',
                'first_name': 'Ana',
                'last_name': 'López',
                'rol': 'cliente',
                'is_staff': False,
            },
            {
                'username': 'cliente2',
                'email': 'cliente2@email.com',
                'password': 'cliente123',
                'first_name': 'Miguel',
                'last_name': 'Fernández',
                'rol': 'cliente',
                'is_staff': False,
            },
            {
                'username': 'cliente3',
                'email': 'cliente3@email.com',
                'password': 'cliente123',
                'first_name': 'Sofía',
                'last_name': 'Ruiz',
                'rol': 'cliente',
                'is_staff': False,
            },
        ]

        for datos in datos_usuarios:
            rol = datos.pop('rol')
            password = datos.pop('password')
            is_staff = datos.pop('is_staff')
            is_superuser = datos.pop('is_superuser', False)

            usuario, creado = User.objects.get_or_create(
                username=datos['username'],
                defaults={**datos, 'is_staff': is_staff, 'is_superuser': is_superuser}
            )

            if creado:
                # set_password() hashea la contraseña correctamente.
                # Nunca almacenes contraseñas en texto plano.
                usuario.set_password(password)
                usuario.save()

                # Creamos el rol asociado
                UserRole.objects.get_or_create(user=usuario, defaults={'role': rol})
                usuarios_creados.append(usuario)
                self.stdout.write(f'   + {usuario.username} ({rol})')
            else:
                self.stdout.write(f'   · {usuario.username} ya existía, omitido.')

        return usuarios_creados

    def _crear_proveedores(self):
        """Crea proveedores de suministros informáticos."""
        self.stdout.write('\n🏭 Creando proveedores...')

        datos_proveedores = [
            {
                'nombre_empresa': 'TechDistributor S.L.',
                'cif': 'B12345678',
                'telefono': '+34 91 234 5678',
                'email': 'contacto@techdistributor.es',
                'direccion': 'Calle Tecnología, 45',
                'ciudad': 'Madrid',
                'codigo_postal': '28001',
                'pais': 'España',
                'persona_contacto': 'Roberto Díaz',
                'descuento_porcentaje': Decimal('5.00'),
                'iva': Decimal('21.00'),
            },
            {
                'nombre_empresa': 'ComponentesPro S.A.',
                'cif': 'A87654321',
                'telefono': '+34 93 876 5432',
                'email': 'ventas@componentespro.es',
                'direccion': 'Avda. Industrial, 12',
                'ciudad': 'Barcelona',
                'codigo_postal': '08001',
                'pais': 'España',
                'persona_contacto': 'Elena Vidal',
                'descuento_porcentaje': Decimal('8.50'),
                'iva': Decimal('21.00'),
            },
            {
                'nombre_empresa': 'InfoSuministros Europa GmbH',
                'cif': 'ESB99887766',
                'telefono': '+49 89 1234 5678',
                'email': 'es@infosuministros.de',
                'direccion': 'Industriestrasse 23',
                'ciudad': 'Múnich',
                'codigo_postal': '80331',
                'pais': 'Alemania',
                'persona_contacto': 'Klaus Weber',
                'descuento_porcentaje': Decimal('12.00'),
                'iva': Decimal('21.00'),
            },
            {
                'nombre_empresa': 'Periféricos del Sur S.L.',
                'cif': 'B55443322',
                'telefono': '+34 95 555 1234',
                'email': 'info@perifericossur.es',
                'direccion': 'Polígono Industrial Sur, Nave 7',
                'ciudad': 'Sevilla',
                'codigo_postal': '41001',
                'pais': 'España',
                'persona_contacto': 'Carmen Morales',
                'descuento_porcentaje': Decimal('3.00'),
                'iva': Decimal('21.00'),
            },
        ]

        proveedores = []
        for datos in datos_proveedores:
            proveedor, creado = Proveedor.objects.get_or_create(
                cif=datos['cif'],
                defaults=datos
            )
            if creado:
                self.stdout.write(f'   + {proveedor.nombre_empresa}')
            else:
                self.stdout.write(f'   · {proveedor.nombre_empresa} ya existía.')
            proveedores.append(proveedor)

        return proveedores

    def _crear_productos(self, proveedores):
        """
        Crea productos de suministros informáticos.

        Usamos zip() para emparejar cada producto con un proveedor
        de forma cíclica con itertools, pero aquí lo hacemos
        simplemente por índice con % (módulo) para no importar más módulos.

        producto_index % len(proveedores) hace que los índices
        0,1,2,3,4,5... se conviertan en 0,1,2,3,0,1... ciclando.
        """
        self.stdout.write('\n📦 Creando productos...')

        datos_productos = [
            {
                'nombre': 'Disco Duro SSD 1TB Samsung 870 EVO',
                'numero_referencia': 'SSD-SAM-1TB-870',
                'descripcion': 'SSD SATA III de 2.5 pulgadas con velocidad de lectura de 560 MB/s. Ideal para actualizar portátiles y ordenadores de sobremesa.',
                'categoria': 'hardware',
                'precio_compra': Decimal('65.00'),
                'precio_venta': Decimal('89.99'),
                'stock_actual': 45,
                'stock_minimo': 20,
                'ubicacion_almacen': 'Estantería A-12',
                'color': 'Negro',
                'especificaciones': 'Interfaz: SATA III\nCapacidad: 1TB\nVelocidad lectura: 560 MB/s\nVelocidad escritura: 530 MB/s\nFactor de forma: 2.5"',
                'proveedor_idx': 0,
            },
            {
                'nombre': 'Memoria RAM DDR4 16GB Kingston',
                'numero_referencia': 'RAM-KING-16GB-DDR4',
                'descripcion': 'Módulo de memoria RAM DDR4 de 3200MHz. Compatible con la mayoría de placas base de última generación.',
                'categoria': 'memorias',
                'precio_compra': Decimal('38.00'),
                'precio_venta': Decimal('54.99'),
                'stock_actual': 8,     # Stock bajo para probar la alerta
                'stock_minimo': 15,
                'ubicacion_almacen': 'Estantería B-03',
                'color': 'Verde',
                'especificaciones': 'Tipo: DDR4\nCapacidad: 16GB\nVelocidad: 3200MHz\nLatencia: CL16\nVoltaje: 1.35V',
                'proveedor_idx': 1,
            },
            {
                'nombre': 'Teclado Mecánico Logitech G413',
                'numero_referencia': 'TEC-LOG-G413-MEC',
                'descripcion': 'Teclado mecánico gaming con switches Romer-G Tactile. Retroiluminación LED blanca y construcción en aluminio cepillado.',
                'categoria': 'accesorios',
                'precio_compra': Decimal('55.00'),
                'precio_venta': Decimal('79.99'),
                'stock_actual': 22,
                'stock_minimo': 10,
                'ubicacion_almacen': 'Estantería C-07',
                'color': 'Plata',
                'especificaciones': 'Switch: Romer-G Tactile\nConexión: USB\nRetroiluminación: LED blanca\nMaterial: Aluminio\nLayout: Español',
                'proveedor_idx': 3,
            },
            {
                'nombre': 'Monitor LG 27" 4K IPS',
                'numero_referencia': 'MON-LG-27-4K-IPS',
                'descripcion': 'Monitor profesional de 27 pulgadas con resolución 4K UHD. Panel IPS con 99% sRGB. Ideal para diseño gráfico y edición de vídeo.',
                'categoria': 'hardware',
                'precio_compra': Decimal('280.00'),
                'precio_venta': Decimal('399.99'),
                'stock_actual': 3,     # Stock muy bajo
                'stock_minimo': 5,
                'ubicacion_almacen': 'Zona Grande G-01',
                'color': 'Negro mate',
                'especificaciones': 'Tamaño: 27"\nResolución: 3840x2160 (4K)\nPanel: IPS\nTasa refresco: 60Hz\nConectividad: HDMI x2, DisplayPort, USB-C',
                'proveedor_idx': 0,
            },
            {
                'nombre': 'Ratón Inalámbrico Logitech MX Master 3',
                'numero_referencia': 'RAT-LOG-MX3-WIRE',
                'descripcion': 'Ratón inalámbrico premium para productividad. Sensor de 4000 DPI, rueda de desplazamiento electromagnética y hasta 70 días de batería.',
                'categoria': 'accesorios',
                'precio_compra': Decimal('68.00'),
                'precio_venta': Decimal('99.99'),
                'stock_actual': 30,
                'stock_minimo': 12,
                'ubicacion_almacen': 'Estantería C-08',
                'color': 'Gris grafito',
                'especificaciones': 'Sensor: 200-4000 DPI\nConexión: Bluetooth / USB receptor\nBatería: 70 días\nBotones: 7 programables',
                'proveedor_idx': 3,
            },
            {
                'nombre': 'Cable HDMI 2.1 2m Vention',
                'numero_referencia': 'CAB-HDMI-2M-21',
                'descripcion': 'Cable HDMI 2.1 de alta velocidad. Soporta resolución hasta 8K a 60Hz y 4K a 120Hz. Ideal para consolas de última generación.',
                'categoria': 'cables',
                'precio_compra': Decimal('8.00'),
                'precio_venta': Decimal('14.99'),
                'stock_actual': 120,
                'stock_minimo': 50,
                'ubicacion_almacen': 'Estantería D-01',
                'color': 'Negro',
                'especificaciones': 'Versión: HDMI 2.1\nLongitud: 2 metros\nAncho de banda: 48Gbps\nResolución máx: 8K@60Hz',
                'proveedor_idx': 2,
            },
            {
                'nombre': 'Fuente de Alimentación Corsair 650W 80+ Gold',
                'numero_referencia': 'FUA-COR-650W-GOLD',
                'descripcion': 'Fuente de alimentación modular de 650W con certificación 80+ Gold. Ventilador de 120mm semi-fanless.',
                'categoria': 'fuentes',
                'precio_compra': Decimal('75.00'),
                'precio_venta': Decimal('109.99'),
                'stock_actual': 14,
                'stock_minimo': 8,
                'ubicacion_almacen': 'Estantería A-05',
                'color': 'Negro',
                'especificaciones': 'Potencia: 650W\nCertificación: 80+ Gold\nModular: Semi-modular\nVentilador: 120mm',
                'proveedor_idx': 1,
            },
            {
                'nombre': 'Antivirus Kaspersky Total Security 3 PCs',
                'numero_referencia': 'SW-KAS-TOT-3PC-1A',
                'descripcion': 'Licencia anual de Kaspersky Total Security para 3 dispositivos. Incluye antivirus, firewall, gestor de contraseñas y VPN.',
                'categoria': 'software',
                'precio_compra': Decimal('22.00'),
                'precio_venta': Decimal('39.99'),
                'stock_actual': 5,    # Stock bajo para probar la alerta
                'stock_minimo': 10,
                'ubicacion_almacen': 'Digital - Sin ubicación física',
                'color': '',
                'especificaciones': 'Dispositivos: 3\nDuración: 1 año\nSistemas: Windows, Mac, Android, iOS\nIncluye: VPN, gestor contraseñas',
                'proveedor_idx': 2,
            },
            {
                'nombre': 'Hub USB-C 7 en 1 Anker',
                'numero_referencia': 'HUB-ANK-7EN1-USBC',
                'descripcion': 'Hub USB-C con 7 puertos: HDMI 4K, USB-A x3, USB-C PD 100W, lector SD y microSD. Compatible con MacBook, iPad Pro y portátiles modernos.',
                'categoria': 'accesorios',
                'precio_compra': Decimal('28.00'),
                'precio_venta': Decimal('44.99'),
                'stock_actual': 35,
                'stock_minimo': 15,
                'ubicacion_almacen': 'Estantería C-12',
                'color': 'Gris espacial',
                'especificaciones': 'Puertos: HDMI, USB-A x3, USB-C PD 100W, SD, microSD\nCompatibilidad: USB-C universal\nSalida vídeo: 4K@30Hz',
                'proveedor_idx': 2,
            },
            {
                'nombre': 'Pasta Térmica Arctic MX-4 4g',
                'numero_referencia': 'PAS-ARC-MX4-4G',
                'descripcion': 'Pasta térmica de alta conductividad. Sin electricidad, no corrosiva y de larga duración. Incluye espátula de aplicación.',
                'categoria': 'otros',
                'precio_compra': Decimal('5.00'),
                'precio_venta': Decimal('8.99'),
                'stock_actual': 80,
                'stock_minimo': 30,
                'ubicacion_almacen': 'Estantería E-02',
                'color': 'Gris',
                'especificaciones': 'Conductividad: 8.5 W/mK\nViscosidad: 870 poise\nTemperatura operación: -50°C a +160°C\nContenido: 4 gramos',
                'proveedor_idx': 1,
            },
        ]

        productos = []
        for datos in datos_productos:
            proveedor_idx = datos.pop('proveedor_idx')
            proveedor = proveedores[proveedor_idx % len(proveedores)]

            producto, creado = Producto.objects.get_or_create(
                numero_referencia=datos['numero_referencia'],
                defaults={**datos, 'proveedor': proveedor}
            )
            if creado:
                self.stdout.write(f'   + {producto.nombre}')
            else:
                self.stdout.write(f'   · {producto.nombre} ya existía.')
            productos.append(producto)

        return productos

    def _crear_ventas(self, usuarios, productos):
        """
        Crea ventas de los últimos 12 meses para que la gráfica tenga datos.

        Distribuimos las ventas en el pasado usando timedelta.
        timedelta(days=N) permite restar N días a una fecha.

        Como fecha_venta usa auto_now_add=True, no podemos establecerla
        directamente al crear. Usamos update() tras la creación para
        forzar la fecha histórica.
        """
        self.stdout.write('\n🛒 Creando ventas históricas...')

        # Filtramos solo usuarios con rol cliente para asignarles ventas
        clientes = User.objects.filter(role__role='cliente')
        if not clientes.exists():
            self.stdout.write(self.style.WARNING('   Sin clientes, omitiendo ventas.'))
            return []

        ventas_creadas = []
        contador = 1

        # Creamos ventas distribuidas en los últimos 12 meses
        # Cada mes tendrá entre 2 y 5 ventas para que la gráfica sea variada
        hoy = datetime.date.today()

        for meses_atras in range(12, 0, -1):
            # Calculamos el primer día del mes correspondiente
            mes = hoy.month - meses_atras
            anio = hoy.year
            while mes <= 0:
                mes += 12
                anio -= 1

            # Número de ventas aleatorio para ese mes (entre 2 y 5)
            num_ventas = random.randint(2, 5)

            for _ in range(num_ventas):
                producto = random.choice(productos)
                cliente = random.choice(list(clientes))
                cantidad = random.randint(1, 5)
                numero_venta = f'VEN-{anio}{mes:02d}-{contador:04d}'

                venta, creado = Venta.objects.get_or_create(
                    numero_venta=numero_venta,
                    defaults={
                        'cliente': cliente,
                        'producto': producto,
                        'cantidad': cantidad,
                        'precio_unitario': producto.precio_venta,
                        'descuento_aplicado': Decimal(random.choice(['0', '5', '10'])),
                        'estado': 'completada',
                    }
                )

                if creado:
                    # Forzamos la fecha histórica con update()
                    # update() modifica directamente en BD sin pasar por save()
                    # lo que evita que auto_now_add lo sobreescriba
                    fecha_venta = timezone.make_aware(
                        datetime.datetime(anio, mes, random.randint(1, 28))
                    )
                    Venta.objects.filter(pk=venta.pk).update(fecha_venta=fecha_venta)
                    ventas_creadas.append(venta)

                contador += 1

        self.stdout.write(f'   + {len(ventas_creadas)} ventas creadas en los últimos 12 meses')
        return ventas_creadas

    def _crear_compras(self, proveedores, productos):
        """Crea compras a proveedores de los últimos 6 meses."""
        self.stdout.write('\n🏭 Creando compras a proveedores...')

        compras_creadas = []
        contador = 1
        hoy = datetime.date.today()

        for meses_atras in range(6, 0, -1):
            mes = hoy.month - meses_atras
            anio = hoy.year
            while mes <= 0:
                mes += 12
                anio -= 1

            num_compras = random.randint(1, 3)

            for _ in range(num_compras):
                producto = random.choice(productos)
                proveedor = producto.proveedor
                cantidad = random.randint(10, 50)
                numero_factura = f'FAC-{anio}{mes:02d}-{contador:04d}'

                compra, creada = CompraProveedor.objects.get_or_create(
                    numero_factura=numero_factura,
                    defaults={
                        'proveedor': proveedor,
                        'producto': producto,
                        'cantidad': cantidad,
                        'precio_unitario': producto.precio_compra,
                        'estado': 'recibida',
                    }
                )

                if creada:
                    fecha_compra = timezone.make_aware(
                        datetime.datetime(anio, mes, random.randint(1, 28))
                    )
                    CompraProveedor.objects.filter(pk=compra.pk).update(
                        fecha_compra=fecha_compra
                    )
                    compras_creadas.append(compra)

                contador += 1

        self.stdout.write(f'   + {len(compras_creadas)} compras a proveedores creadas')
