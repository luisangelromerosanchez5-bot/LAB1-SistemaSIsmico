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
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

def generar_pdf_explicacion():
    pdf_path = os.path.join("docs", "Explicacion_Arquitectura_BD_y_Flutter.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Estilos 100% NEGRO (#000000 / colors.black)
    titulo_style = ParagraphStyle(
        'TituloNegro',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.black,
        alignment=TA_CENTER,
        spaceAfter=8,
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
        fontSize=12,
        leading=16,
        textColor=colors.black,
        spaceBefore=12,
        spaceAfter=6,
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

    # --- PORTADA ---
    story.append(Paragraph("GUÍA EXPLICATIVA DE ARQUITECTURA Y BASES DE DATOS", titulo_style))
    story.append(Paragraph("P1 · BITÁCORA SÍSMICA CEET", ParagraphStyle('SubSub', parent=titulo_style, fontSize=14, leading=18, spaceAfter=4)))
    story.append(Paragraph("SENA · ADSO · Guía de Conceptos, Conexiones de Base de Datos y Funcionamiento Móvil", subtitulo_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.black, spaceAfter=12))

    # --- 1. LAS BASES DE DATOS DEL PROYECTO ---
    story.append(Paragraph("1. ¿Cómo se Manejan las Bases de Datos en el Proyecto?", h1_style))
    story.append(Paragraph(
        "El proyecto utiliza una arquitectura de doble base de datos para responder al patrón <b>Offline-First</b> (operación sin conexión a internet):",
        body_style
    ))
    story.append(Paragraph("<b>A. Base de Datos del Celular (SQLite - Local):</b> Vive internamente en la memoria del teléfono inteligente (bitacora_sismica.db). Su función es actuar como una cola de almacenamiento inmediato. Cada vez que el acelerómetro detecta un impacto, el evento se guarda obligatoriamente aquí primero marcándolo como no sincronizado (sincronizado = 0). Si el usuario está sin señal o en Modo Avión, el dato nunca se pierde.", bullet_style))
    story.append(Paragraph("<b>B. Base de Datos del Servidor (PostgreSQL - Nube en Render):</b> Vive de forma centralizada en los servidores de Render (https://bitacora-sismica-api.onrender.com). Guarda el registro histórico oficial de todos los dispositivos y eventos reportados. Contiene las tablas 'dispositivo' (equipos registrados) y 'evento_impacto' (magnitud, severidad, GPS, fecha y hora).", bullet_style))

    story.append(Spacer(1, 8))

    # --- 2. CONEXIÓN ENTRE SQLITE Y POSTGRESQL ---
    story.append(Paragraph("2. ¿Cómo se Conecta SQLite con PostgreSQL en Render?", h1_style))
    story.append(Paragraph(
        "SQLite y PostgreSQL <b>NO están conectados directamente entre sí</b>. La aplicación móvil desarrollada en Flutter actúa como el intermediario o puente inteligente:",
        body_style
    ))
    story.append(Paragraph("1. La App lee de SQLite local los eventos pendientes con sincronizado = 0.", bullet_style))
    story.append(Paragraph("2. La App convierte el evento a formato JSON y lo transmite por internet mediante una petición HTTP POST /api/eventos utilizando la librería Dio.", bullet_style))
    story.append(Paragraph("3. La API en FastAPI (en Render) recibe la petición, valida la estructura y la guarda permanentemente en PostgreSQL.", bullet_style))
    story.append(Paragraph("4. Render responde a la App con código HTTP 200 OK y el ID asignado.", bullet_style))
    story.append(Paragraph("5. La App recibe la confirmación y actualiza la fila en SQLite local marcando sincronizado = 1.", bullet_style))

    story.append(Spacer(1, 8))

    # --- 3. CONCEPTO DE IDEMPOTENCIA ---
    story.append(Paragraph("3. Prevención de Duplicados e Idempotencia (clave_cliente)", h1_style))
    story.append(Paragraph(
        "Antes de guardar un golpe en SQLite, la app genera una cédula única e irrepetible llamada <code>clave_cliente</code> (UUID v4). Si la conexión a internet se interrumpe y la app reintenta el envío 5 veces, la base de datos PostgreSQL en Render verifica la restricción UNIQUE(dispositivo_id, clave_cliente) y rechaza la creación de filas duplicadas, devolviendo el registro existente con código 200/201. Esto garantiza la integridad del histórico sísmico.",
        body_style
    ))

    story.append(Spacer(1, 8))

    # --- 4. FUNCIONAMIENTO DE FLUTTER Y EJECUCIÓN ---
    story.append(Paragraph("4. Funcionamiento de la Aplicación Flutter y Dudas Frecuentes", h1_style))
    
    story.append(Paragraph("4.1. ¿Por qué la app sigue en el celular al desconectar el cable USB?", h1_style))
    story.append(Paragraph(
        "Al ejecutar <code>flutter run</code> con el celular conectado por primera vez, el compilador de Flutter genera el paquete APK instalable e instala la aplicación directamente en el sistema operativo Android de tu teléfono. Por esta razón, la app es 100% independiente: puedes desenchufar el cable, reiniciar el teléfono y abrir la app llamada <i>Bitácora Sísmica CEET</i> desde tu menú de aplicaciones en cualquier momento.",
        body_style
    ))

    story.append(Paragraph("4.2. ¿Qué significa el mensaje 'No supported devices connected'?", h1_style))
    story.append(Paragraph(
        "Ese mensaje es **completamente normal y esperable** cuando ejecutas <code>flutter run</code> en tu PC sin tener el celular físico conectado por cable USB. Simplemente significa que la computadora no detecta ningún teléfono conectado en ese instante para enviarle código nuevo. Dado que la app ya está instalada en la memoria de tu celular, no necesitas volver a ejecutar ese comando a menos que quieras hacer modificaciones al código fuente.",
        body_style
    ))

    # --- CUADRO RESUMEN ---
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Resumen de Operación del Sistema</b>", h1_style))
    summary_data = [
        [Paragraph("<b>Componente</b>", table_header_style), Paragraph("<b>Ubicación</b>", table_header_style), Paragraph("<b>Función Principal</b>", table_header_style)],
        [Paragraph("App Móvil (Flutter)", table_body_style), Paragraph("Celular Físico", table_body_style), Paragraph("Captura acelerómetro (>15m/s²), vibración háptica, consulta GPS y visualización UI.", table_body_style)],
        [Paragraph("SQLite Local", table_body_style), Paragraph("Celular Físico", table_body_style), Paragraph("Cola de persistencia offline (sincronizado=0). Evita pérdida de datos sin red.", table_body_style)],
        [Paragraph("API FastAPI", table_body_style), Paragraph("Nube (Render.com)", table_body_style), Paragraph("Endpoints REST (/api/eventos), validación Pydantic e idempotencia.", table_body_style)],
        [Paragraph("PostgreSQL", table_body_style), Paragraph("Nube (Render.com)", table_body_style), Paragraph("Base de datos centralizada con el histórico completo de impactos.", table_body_style)],
    ]
    summary_table = Table(summary_data, colWidths=[110, 110, 280])
    summary_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(summary_table)

    # Construir PDF
    doc.build(story)
    print("PDF explicativo generado exitosamente en:", pdf_path)

if __name__ == '__main__':
    generar_pdf_explicacion()
