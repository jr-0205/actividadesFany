# Práctica_6_1 — Sistema para Banco

**Semana #4 · Práctica 6 · Parcial 1**  
**Fecha indicada en la actividad:** martes 22 de septiembre de 2026.

## Objetivo

Desarrollar un sistema bancario funcional que integre los puntos indicados en clase: **agentes, base de datos, diseño y funcionalidad**, además de las principales operaciones mostradas en el esquema de la práctica.

## Funciones incluidas

### No. de cuenta y cliente asociado
- Número de cuenta.
- Nombre del cliente.
- Correo.
- Teléfono.
- Saldo disponible.
- Tarjeta de débito asociada.

### Tarjeta de débito
- Consultar saldo.
- Realizar depósitos.
- Realizar retiros.
- Realizar transferencias entre cuentas.
- Guardar cada movimiento en SQLite.
- Validar saldo suficiente y cuenta destino.
- Ejecutar la transferencia como una sola transacción atómica: si algo falla, ningún saldo cambia.
- Mostrar saldo anterior y saldo posterior después de cada operación.

### Tarjeta de crédito
- Línea de crédito aprobada.
- Crédito disponible.
- Saldo utilizado.
- Fecha de corte.
- Fecha de pago límite.
- Alerta automática cuando faltan 5 días o menos para el pago límite.
- Pago mínimo.
- Pago total.
- Registrar compras.
- Registrar pagos.

### Préstamos
- Bancario.
- Hipotecario.
- Vehicular.
- Cálculo de pago mensual estimado.
- Registro de solicitud en la base de datos.

Las tasas incluidas son valores de demostración para la práctica académica, no ofertas financieras reales.

### Seguros
- Vida.
- Auto.
- Patrimonio — Casa.
- Patrimonio — Empresa.
- Médico.
- Registro de póliza y prima mensual.

Las primas y coberturas son datos ficticios para demostrar el funcionamiento del sistema.

## Agentes del sistema

El proyecto separa las reglas del negocio en agentes especializados:

1. **Coordinador:** recibe la operación y muestra la trazabilidad.
2. **Cliente:** valida la cuenta asociada.
3. **Débito:** procesa depósitos, retiros y transferencias.
4. **Crédito:** procesa compras y pagos de tarjeta.
5. **Préstamos:** valida el tipo, monto y plazo; calcula la mensualidad.
6. **Seguros:** registra la protección seleccionada.

Cada operación importante deja evidencia en la base de datos.

## Tecnologías

- Python 3.10+
- Flask
- SQLite
- HTML5
- CSS3
- JavaScript

## Instalación y ejecución

En PowerShell:

    cd "Práctica_6_1"
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    python app.py

Después abre en el navegador:

    http://127.0.0.1:5000

La base de datos banco.db se crea automáticamente al iniciar.

## Datos de demostración

El sistema inicia con dos cuentas ficticias:

- Cuenta principal: 1002003001
- Cuenta destino para transferencias: 1002003002

Esto permite demostrar una transferencia sin tener que capturar clientes manualmente. El botón **Cambiar cuenta** alterna entre ambas cuentas para comprobar inmediatamente que el dinero salió de una y entró en la otra.

## Prueba rápida

1. Abre el panel y muestra los datos del cliente y el número de cuenta.
2. Enseña el saldo y la tarjeta de débito.
3. Realiza un depósito.
4. Realiza un retiro.
5. Ejecuta una transferencia hacia la segunda cuenta.
6. En crédito, muestra línea aprobada, corte, pago límite, pago mínimo y total.
7. Registra una compra o un pago de tarjeta.
8. Solicita un préstamo.
9. Contrata un seguro.
10. Muestra los movimientos guardados y la trazabilidad de los agentes.

El botón **Restaurar datos de prueba** deja el sistema listo para repetir la demostración.

## Estructura

    Práctica_6_1/
    ├── app.py
    ├── agents.py
    ├── database.py
    ├── requirements.txt
    ├── README.md
    ├── GUION_VIDEO.md
    ├── templates/
    │   └── index.html
    └── static/
        ├── app.js
        └── styles.css

## Nota académica

El sistema es una simulación educativa. No procesa dinero real, no se conecta con instituciones financieras y los datos de tasas, coberturas, tarjetas y clientes son ficticios.


## Reglas de integridad de saldos

- Ningún saldo de débito puede quedar por debajo de cero.
- Los montos deben ser mayores a cero.
- Una transferencia no puede enviarse a la misma cuenta origen.
- La cuenta origen y la cuenta destino deben existir.
- El retiro de la cuenta origen y el depósito en la cuenta destino se confirman juntos.
- Cada transferencia genera dos movimientos: salida en origen y entrada en destino.
- Un pago de tarjeta de crédito descuenta el dinero de la cuenta de débito asociada y reduce la deuda de crédito en la misma operación.
- La línea de crédito no puede ser excedida.
- Los datos iniciales son consistentes: la cuenta 1002003001 inicia con $12,500.00 y la 1002003002 con $5,000.00.

## Pruebas automáticas

Desde la carpeta de la práctica puedes validar las reglas principales con:

    python -m unittest discover -s tests -v

Las pruebas comprueban:

- Transferencia de $1,000: 12,500 → 11,500 y 5,000 → 6,000.
- Rechazo y rollback cuando el saldo es insuficiente.
- Consistencia entre pago de crédito y saldo de débito.
- Saldos iniciales de las dos cuentas demo.
