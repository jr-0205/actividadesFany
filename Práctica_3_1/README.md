# Práctica 3_1P — Sistema de inscripción a club deportivo

Aplicación web individual con **arquitectura multi-agente** y **base de datos SQLite**. El sistema digitaliza el proceso descrito en clase: recibe una solicitud de inscripción, consulta disciplinas y horarios, valida requisitos, calcula costos y genera una confirmación final.

## Agentes implementados

1. **Coordinador**: recibe la solicitud y organiza el flujo.
2. **Registro**: recopila, limpia y normaliza los datos.
3. **Validación**: verifica edad, contacto, tutor y duplicados.
4. **Deportes**: consulta disciplinas disponibles según la edad.
5. **Horarios**: consulta horarios compatibles y cupos reales.
6. **Costos**: calcula inscripción, mensualidad y descuento.
7. **Confirmación**: guarda la inscripción en SQLite y genera el folio/credencial.

La clasificación usada sigue el apunte de clase:

- Mujer: 18 años o más.
- Hombre: 18 años o más.
- Niña: 6 a 17 años.
- Niño: 6 a 17 años.

Los menores de edad reciben **15 % de descuento en la primera mensualidad** y deben capturar datos de tutor.

## Tecnologías

- Python 3.10+
- Flask
- HTML5 + CSS3 + JavaScript
- SQLite

No necesita una API externa ni una clave de IA: los agentes son componentes inteligentes especializados basados en reglas de negocio y trabajan coordinados por un agente principal. Esto hace que la práctica sea reproducible en cualquier PC.

## Ejecutar

```bash
cd "Práctica_3_1P"
python -m venv .venv
```

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

### Linux/macOS

```bash
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abre en el navegador:

```text
http://127.0.0.1:5000
```

La base `club_deportivo.db` se crea automáticamente al iniciar por primera vez y se llena con disciplinas y horarios de ejemplo.

## Prueba rápida para demostrar

1. Captura nombre, edad, sexo, correo y teléfono.
2. El sistema asigna automáticamente la categoría.
3. Elige una disciplina y un horario con cupo.
4. Si la persona es menor, captura también los datos del tutor.
5. Pulsa **Procesar con agentes**.
6. Observa a los siete agentes marcando el flujo como correcto.
7. Muestra el folio, la credencial, el cálculo del primer pago y el registro guardado en la tabla inferior.

## Estructura

```text
Práctica_3_1P/
├── app.py
├── agents.py
├── database.py
├── requirements.txt
├── README.md
├── GUION_VIDEO.md
├── static/
│   ├── app.js
│   └── styles.css
└── templates/
    └── index.html
```
