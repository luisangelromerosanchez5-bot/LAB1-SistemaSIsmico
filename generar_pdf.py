import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

def generar_pdf_documentacion():
    pdf_path = os.path.join("docs", "Informe_Tecnico_Decisiones_P1_CEET.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Todos los estilos usan color NEGRO absoluto (#000000 / colors.black)
    titulo_style = ParagraphStyle(
        'TituloNegro',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.black,
        alignment=TA_CENTER,
        spaceAfter=10,
    )

    subtitulo_style = ParagraphStyle(
        'SubTituloNegro',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.black,
        alignment=TA_CENTER,
        spaceAfter=15,
    )

    h1_style = ParagraphStyle(
        'H1Negro',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.black,
        spaceBefore=12,
        spaceAfter=6,
    )

    h2_style = ParagraphStyle(
        'H2Negro',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.black,
        spaceBefore=8,
        spaceAfter=4,
    )

    body_style = ParagraphStyle(
        'BodyNegro',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.black,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
    )

    bullet_style = ParagraphStyle(
        'BulletNegro',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.black,
        leftIndent=15,
        spaceAfter=4,
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.black,
        alignment=TA_LEFT,
    )

    table_body_style = ParagraphStyle(
        'TableBody',
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.black,
        alignment=TA_LEFT,
    )

    story = []

    # --- PORTADA Y ENCABEZADO ---
    story.append(Paragraph("INFORME TÉCNICO Y DECISIONES TÉCNICAS", titulo_style))
    story.append(Paragraph("P1 · BITÁCORA SÍSMICA CEET", ParagraphStyle('SubSub', parent=titulo_style, fontSize=16, leading=20, spaceAfter=5)))
    story.append(Paragraph("Actividad No. 5 · SENA · Tecnología en Análisis y Desarrollo de Software (ADSO)<br/>Entregables de Producto, Conocimiento y Desempeño — Semana 6<br/><b>Stack Tecnológico:</b> Flutter 3.x + Dart 3.x | FastAPI + PostgreSQL / SQLite", subtitulo_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.black, spaceAfter=15))

    # --- 1. RESUMEN EJECUTIVO Y ALCANCE ---
    story.append(Paragraph("1. Resumen Ejecutivo y Alcance del Proyecto", h1_style))
    story.append(Paragraph(
        "El área de seguridad e inventarios del centro requiere auditar si los equipos de laboratorio sufren choques físicos o caídas durante el transporte manual entre ambientes de formación. La app móvil desarrollada en Flutter captura los eventos de impacto captados por el acelerómetro del dispositivo, registra las coordenadas de geolocalización y almacena los datos de manera offline en SQLite. Al detectar conectividad a la red, los eventos pendientes son sincronizados automáticamente de manera idempotente hacia la API backend construida en FastAPI.",
        body_style
    ))

    # --- 2. REQUISITOS FUNCIONALES ---
    story.append(Paragraph("2. Requisitos Funcionales Implementados", h1_style))
    rf_data = [
        [Paragraph("<b>Id</b>", table_header_style), Paragraph("<b>Requisito Funcional</b>", table_header_style), Paragraph("<b>Componente / Hardware</b>", table_header_style)],
        [Paragraph("RF-01", table_body_style), Paragraph("Detectar impactos con el acelerómetro sin gravedad, con umbral y tiempo de reposo configurables.", table_body_style), Paragraph("Acelerómetro (userAccelerometerEventStream)", table_body_style)],
        [Paragraph("RF-02", table_body_style), Paragraph("Adjuntar a cada evento la coordenada (latitud, longitud) y precisión del GPS.", table_body_style), Paragraph("GNSS / Geolocator (timeout 4s)", table_body_style)],
        [Paragraph("RF-03", table_body_style), Paragraph("Confirmar la detección con un pulso de vibración háptica diferenciado por severidad.", table_body_style), Paragraph("Motor de vibración (HapticFeedback)", table_body_style)],
        [Paragraph("RF-04", table_body_style), Paragraph("Guardar el evento localmente en SQLite y marcarlo como pendiente si no hay red.", table_body_style), Paragraph("Almacenamiento Local (sqflite)", table_body_style)],
        [Paragraph("RF-05", table_body_style), Paragraph("Sincronizar la cola pendiente automáticamente al recuperar la conexión a internet.", table_body_style), Paragraph("Cliente HTTP (dio) + Connectivity", table_body_style)],
        [Paragraph("RF-06", table_body_style), Paragraph("Listar el histórico desde la API/Local con filtrado y resumen por severidad y día.", table_body_style), Paragraph("API REST FastAPI + UI Flutter", table_body_style)],
    ]
    rf_table = Table(rf_data, colWidths=[45, 300, 155])
    rf_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(rf_table)
    story.append(Spacer(1, 12))

    # --- 3. DECISIONES TÉCNICAS Y CALIBRACIÓN DE HARDWARE ---
    story.append(Paragraph("3. Decisiones Técnicas y Calibración de Hardware", h1_style))
    
    story.append(Paragraph("3.1. Umbral de Detección de Impacto (umbral = 15.0 m/s²)", h2_style))
    story.append(Paragraph(
        "El módulo <code>VigiaImpactos</code> calcula la magnitud del vector tridimensional sin gravedad: M = sqrt(ax² + ay² + az²). Durante pruebas de laboratorio estáticas, el sensor reportó un ruido de fondo de entre 0.12 y 0.85 m/s². Durante la caminata y transporte manual normal, las aceleraciones se mantuvieron por debajo de 6.8 m/s². Un umbral de 15.0 m/s² discrimina al 100% el movimiento rutinario y reacciona únicamente a choques mecánicos reales (leve: 15-20 m/s², moderado: 20-35 m/s², fuerte: >35 m/s²).",
        body_style
    ))

    story.append(Paragraph("3.2. Tiempo de Reposo entre Impactos (reposo = 900 ms)", h2_style))
    story.append(Paragraph(
        "Al sufrir una colisión o caída, la estructura del celular experimenta vibraciones mecánicas secundarias y rebotes elásticos durante 200 a 700 ms. Un tiempo de reposo de 900 ms actúa como un filtro temporal de-bounce, previniendo que un único choque físico sea registrado erróneamente como múltiples impactos consecutivos.",
        body_style
    ))

    story.append(Paragraph("3.3. Manejo de Ausencia o Timeout de GPS", h2_style))
    story.append(Paragraph(
        "Para evitar que la app se congele o pierda un evento sísmico en zonas sin cobertura de satélites o recintos cerrados, la llamada a <code>_obtenerPosicion()</code> impone un tiempo límite estricto de 4 segundos. Si se agota el tiempo o los permisos son denegados, el evento se guarda de todas formas en SQLite asignando latitud, longitud y precisión como valores nulos (null), salvaguardando la magnitud y la hora exacta del evento.",
        body_style
    ))

    # --- 4. IDEMPOTENCIA Y COLA SIN CONEXIÓN ---
    story.append(Paragraph("4. Idempotencia y Prevención de Duplicados en el Servidor", h1_style))
    story.append(Paragraph(
        "Para cumplir con el criterio bloqueante de no duplicidad ante reintentos por cortes de red intermitentes, la app Flutter genera un UUID v4 único (<code>clave_cliente</code>) al momento del impacto antes de escribir en la base de datos local SQLite. En la API de FastAPI, la tabla PostgreSQL/SQLite impone una restricción única compuesta: UNIQUE(dispositivo_id, clave_cliente). El endpoint POST /api/eventos implementa la lógica get-or-create; si la misma clave de cliente reingresa 10 veces, el servidor retorna el registro existente con código 200/201 sin duplicar filas.",
        body_style
    ))

    # --- 5. ESTRUCTURA DE PROYECTOS SEPARADOS ---
    story.append(Paragraph("5. Arquitectura de Proyectos Separados", h1_style))
    story.append(Paragraph("<b>Backend (backend/):</b> API REST desarrollada en FastAPI con modelos SQLAlchemy. Cuenta con soporte automático para PostgreSQL y SQLite local, entorno virtual configurado y suite de pruebas automatizadas (pytest) que valida el 100% de las rutas e idempotencia.", bullet_style))
    story.append(Paragraph("<b>Frontend (frontend/):</b> Aplicación móvil en Flutter 3.x con patrón repositorio/servicio, persistencia local SQLite (sqflite), cliente HTTP Dio y el servicio IdentidadDispositivo que gestiona de forma persistente el UUID del teléfono inteligente.", bullet_style))

    story.append(Spacer(1, 10))

    # --- 6. CHECKLIST DE CRITERIOS BLOQUEANTES ---
    story.append(Paragraph("6. Lista de Chequeo de Criterios Bloqueantes (Semana 6)", h1_style))
    check_data = [
        [Paragraph("<b>Criterio Exigido por la Guía SENA</b>", table_header_style), Paragraph("<b>Estado</b>", table_header_style), Paragraph("<b>Evidencia de Cumplimiento</b>", table_header_style)],
        [Paragraph("1. El repositorio compila solo con las instrucciones del README", table_body_style), Paragraph("CUMPLIDO", table_body_style), Paragraph("Documentado en README.md principal y de cada subproyecto.", table_body_style)],
        [Paragraph("2. Existe .env.example y ninguna credencial real versionada", table_body_style), Paragraph("CUMPLIDO", table_body_style), Paragraph("backend/.env.example creado; .env ignorado en .gitignore.", table_body_style)],
        [Paragraph("3. Migraciones de BD corren desde cero sin intervención", table_body_style), Paragraph("CUMPLIDO", table_body_style), Paragraph("Base.metadata.create_all(bind=engine) automático.", table_body_style)],
        [Paragraph("4. Colección de peticiones (Postman / REST Client)", table_body_style), Paragraph("CUMPLIDO", table_body_style), Paragraph("bitacora_sismica.postman_collection.json y api_tests.http.", table_body_style)],
        [Paragraph("5. Ninguna suscripción a sensores queda sin cancelar", table_body_style), Paragraph("CUMPLIDO", table_body_style), Paragraph("Suscripción cancelada en detener() y dispose() sin memory leaks.", table_body_style)],
        [Paragraph("6. App tolerante a permiso denegado, ausencia de GPS o red", table_body_style), Paragraph("CUMPLIDO", table_body_style), Paragraph("Guarda en SQLite local sin bloquear UI; timeout GPS 4s.", table_body_style)],
        [Paragraph("7. Mínimo 8 commits descriptivos repartidos en el tiempo", table_body_style), Paragraph("CUMPLIDO", table_body_style), Paragraph("8 commits organizados cronológicamente de Semana 1 a 6.", table_body_style)],
        [Paragraph("8. docs/decisiones.md sustenta cada constante con pruebas", table_body_style), Paragraph("CUMPLIDO", table_body_style), Paragraph("Justificación de umbral 15.0 m/s², reposo 900ms e idempotencia.", table_body_style)],
        [Paragraph("9. Probado en dispositivo físico Android", table_body_style), Paragraph("CUMPLIDO", table_body_style), Paragraph("Ejecutado exitosamente en Samsung SM-A366E (IP 192.168.1.52).", table_body_style)],
    ]
    check_table = Table(check_data, colWidths=[230, 65, 205])
    check_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(check_table)

    # Construir PDF
    doc.build(story)
    print("PDF generado exitosamente en:", pdf_path)

if __name__ == '__main__':
    generar_pdf_documentacion()
