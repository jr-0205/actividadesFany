# Guion de demostración — máximo 2 minutos

**0:00–0:15**

“Esta es mi Práctica 3: un sistema web para inscripción a un club deportivo. Está desarrollado con Flask, JavaScript y SQLite, y utiliza una arquitectura de siete agentes especializados.”

**0:15–0:35**

“Del lado derecho se observan los agentes. El Coordinador recibe la solicitud; Registro organiza los datos; Validación comprueba requisitos; Deportes y Horarios consultan disponibilidad; Costos realiza el cálculo; y Confirmación guarda el resultado en la base de datos.”

**0:35–1:05**

“Voy a registrar un usuario. Capturo nombre, edad, sexo, correo y teléfono. El sistema detecta la categoría automáticamente. Para menores de 18 años también solicita los datos del tutor. Después consulto una disciplina y el sistema solo muestra horarios compatibles con la edad y con lugares disponibles.”

**1:05–1:30**

“Al presionar ‘Procesar con agentes’, el Coordinador ejecuta cada agente. Se validan los datos, la disciplina, el horario y el cupo. El agente de Costos calcula inscripción, mensualidad y descuento. Si todo es correcto, Confirmación genera un folio.”

**1:30–1:50**

“Aquí aparece la credencial digital con nombre, categoría, disciplina, horario y primer pago. Abajo se observa la inscripción guardada, comprobando que sí existe persistencia en la base de datos SQLite.”

**1:50–2:00**

“Con esto se cumple funcionalidad, buen diseño, base de datos y coordinación multi-agente en una aplicación web.”
