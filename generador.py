import streamlit as st
from fpdf import FPDF
from fpdf.enums import XPos, YPos, MethodReturnValue
from datetime import datetime, timedelta
import tempfile
import os
import locale
import random
import string
import hashlib

# --- AUTENTICACIÓN SIMPLE ---
USUARIO_AUTORIZADO = "admin"
PASSWORD_CLARA = "1129"

def hashear_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

PASSWORD_HASH = hashear_password(PASSWORD_CLARA)

def autenticar_usuario():
    st.title("🔐 Acceso restringido")
    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if usuario == USUARIO_AUTORIZADO and hashear_password(password) == PASSWORD_HASH:
            st.session_state["autenticado"] = True
        else:
            st.error("Usuario o contraseña incorrectos.")
       

# --- CONFIGURACIÓN DE LOCALE ---
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')
    except locale.Error:
        st.warning("No se pudo establecer el locale a español.")

# --- GENERADOR DE NÚMERO DE PRESUPUESTO AUTOMÁTICO ---
def generar_num_presupuesto():
    fecha = datetime.today().strftime("%y%m%d")
    aleatorio = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"KT-{fecha}-{aleatorio}"

# --- DATOS PARA PLANTILLAS DE ITINERARIO (REORGANIZADOS) ---

# Plantillas de Actividades (Ordenadas alfabéticamente)
PLANTILLAS_ACTIVIDADES = [
    "--- Escribir manualmente ---",
    "Día completo de safari en el Parque Nacional de Amboseli, famoso por sus grandes manadas de elefantes con el Kilimanjaro de fondo.",
    "Día completo de safari en el Parque Nacional del Lago Nakuru, famoso por sus flamencos y rinocerontes.",
    "Día completo de safari en Masái Mara, buscando a los 'Cinco Grandes'. Almuerzo tipo pícnic a orillas del río Mara.",
    "Día libre en Nairobi y traslado al aeropuerto para el vuelo de regreso.",
    "Llegada a Nairobi, traslado al hotel y tiempo libre. Dependiendo de la hora, se pueden visitar museos o parques locales.",
    "Safari en el Parque Nacional de Naivasha, incluyendo un paseo en barco para observar hipopótamos y aves.",
    "Safari matutino en Amboseli y viaje de regreso a Nairobi.",
    "Safari matutino en Lago Nakuru y viaje hacia el Lago Naivasha.",
    "Tour por Nairobi: visita al mercado Masái para compras y tiempo libre en la ciudad.",
    "Viaje de Amboseli a Naivasha, llegada al hotel y tour en barco por el lago para ver hipopótamos y aves.",
    "Viaje de Nairobi a Amboseli, safari al atardecer y vistas al Kilimanjaro.",
    "Viaje de Nairobi a Masái Mara (4-5 horas). Check-in en el hotel y safari al atardecer.",
    "Viaje de Nakuru a Masái Mara. Check-in en el hotel y safari durante el atardecer.",
    "Viaje de Naivasha al Parque Nacional de Amboseli, con las vistas del Kilimanjaro.",
    "Visita a los proyectos sociales de Soweto Youth Initiative y Under Lea’s Trust.",
    "Visita a un poblado Masái para conocer su cultura. Posteriormente, viaje hacia el Lago Nakuru.",
    "Visita al Orfanato de Elefantes de Sheldrick y al Centro de Jirafas de AFEW.",
]

# Plantillas de Hoteles (Agrupados por ubicación)
HOTELES_POR_ZONA = {
    "Amboseli": [
        "AA Lodge Amboseli",
        "Nyati Amboseli Camp",
        "Manjaro Camp",
    ],
    "Masai Mara": [
        "Sankare Mara Camp",
        "Lenchada Mara Camp",
        "Jambo Mara Camp",
    ],
    "Nairobi": [
        "Nairobi Airport Landing Hotel",
        "After 40 Hotel",
    ],
    "Nakuru": [
        "Buraha Zenoni Hotel",
        "Nakuru Lodge",
    ],
    "Naivasha": [
        "Chambai Hotel",
        "Dove Nest Hotel",
    ],
    "Otros": [
        "Alojamiento en tiendas (tipo campamento)",
    ]
}

# Crear una lista plana para el selectbox con cabeceras no seleccionables
PLANTILLAS_HOTELES_FLAT = ["--- Escribir manualmente o vacío último día---"]
for zona, hoteles in HOTELES_POR_ZONA.items():
    PLANTILLAS_HOTELES_FLAT.append(f"--- {zona.upper()} ---")
    for hotel in sorted(hoteles):
        PLANTILLAS_HOTELES_FLAT.append(hotel)

# --- CONFIGURACIÓN DE ESTILO "SAFARI ELEGANTE" ---
# (Sin cambios)
COLOR_TEXTO_PRINCIPAL = (89, 72, 56)
COLOR_FONDO_CABECERA = (232, 222, 204)
COLOR_FILA_ALTERNA = (247, 243, 235)
COLOR_BLANCO = (255, 255, 255)
COLOR_LINEA = (222, 211, 190)
COLOR_TOTAL = (222, 211, 190)
COLOR_CHECKMARK = (85, 107, 47)

FONT_TITULOS = "Cinzel"
FONT_CUERPO = "Lato"

# --- CLASE PDF Y GENERACIÓN DE PDF ---
# (El resto del código para generar el PDF no necesita cambios)
class PDF(FPDF):
    def footer(self):
        self.set_y(-25)
        self.set_font(FONT_CUERPO, '', 10)
        self.set_text_color(*COLOR_LINEA)
        self.cell(0, 10, "◊" * 25, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.set_text_color(150, 135, 115)
        self.cell(0, 8, "Kenia Tours © — info@safarikeniatours.es", align='C')

def draw_itinerary_header(pdf):
    pdf.set_font(FONT_CUERPO, 'B', 11)
    pdf.set_fill_color(*COLOR_FONDO_CABECERA)
    pdf.set_text_color(*COLOR_TEXTO_PRINCIPAL)
    pdf.cell(35, 11, "Día", border=1, fill=True, align='C')
    pdf.cell(155, 11, "Descripción", border=1, fill=True, align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

def generar_pdf(data):
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=30)
    
    try:
        pdf.add_font(FONT_TITULOS, "", os.path.join("fonts", "Cinzel-Regular.ttf"))
        pdf.add_font(FONT_TITULOS, "B", os.path.join("fonts", "Cinzel-Bold.ttf"))
        pdf.add_font(FONT_CUERPO, "", os.path.join("fonts", "Lato-Regular.ttf"))
        pdf.add_font(FONT_CUERPO, "B", os.path.join("fonts", "Lato-Bold.ttf"))
        pdf.add_font(FONT_CUERPO, "I", os.path.join("fonts", "Lato-Italic.ttf"))
        pdf.add_font("DejaVu", "", os.path.join("fonts", "DejaVuSans.ttf"))
    except RuntimeError as e:
        st.error(f"Error al cargar fuentes: {e}. Asegúrate de tener Cinzel, Lato y DejaVuSans en la carpeta 'fonts'.")
        return None

    pdf.set_text_color(*COLOR_TEXTO_PRINCIPAL)

    logo_circulo_path = os.path.join("fonts", "logo_circulo.png")
    logo_texto_path = os.path.join("fonts", "logo_texto.png")
    if os.path.exists(logo_circulo_path):
        pdf.image(logo_circulo_path, x=15, y=10, w=25)
    if os.path.exists(logo_texto_path):
        pdf.image(logo_texto_path, x=45, y=12, w=70)
    pdf.set_font(FONT_TITULOS, 'B', 18)
    pdf.ln(20)
    pdf.cell(0, 25, data["titulo"], new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

    pdf.set_font(FONT_CUERPO, '', 11)
    line_height_datos = 7
    pdf.cell(0, line_height_datos, f"Número de presupuesto: {data['numero_presupuesto']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, line_height_datos, f"Fecha de emisión: {data['fecha_emision']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, line_height_datos, f"Contacto: {data['contacto']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)
    fecha_fin = data["fecha_inicio"] + timedelta(days=data["num_dias"] - 1)
    pdf.cell(0, line_height_datos, f"Régimen de comidas: Pensión completa", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, line_height_datos, f"Fecha estimada del viaje: {data['fecha_inicio'].strftime('%d de %B de %Y')} al {fecha_fin.strftime('%d de %B de %Y')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(12)

    pdf.set_font(FONT_TITULOS, 'B', 14)
    pdf.cell(0, 10, "Itinerario del Viaje", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(3)
    
    draw_itinerary_header(pdf)
    
    col_widths_it = (35, 155)
    line_height_it = 6.5
    fill = True
    for dia in data["itinerario"]:
        day_text = f"{dia['dia']}\n({dia['fecha']})"
        
        # ✅ Modificación: incluir "Noche en:" solo si hay contenido
        desc_text = dia['actividad']
        if dia['noche'].strip():
            desc_text += f"\nNoche en: {dia['noche']}"

        pdf.set_font(FONT_CUERPO, 'B', 10)
        lines_day = pdf.multi_cell(w=col_widths_it[0], h=line_height_it, text=day_text, dry_run=True, output=MethodReturnValue.LINES)
        pdf.set_font(FONT_CUERPO, '', 10)
        lines_desc = pdf.multi_cell(w=col_widths_it[1], h=line_height_it, text=desc_text, dry_run=True, output=MethodReturnValue.LINES)
        row_height = max(len(lines_day), len(lines_desc)) * line_height_it + 6

        if pdf.get_y() + row_height > pdf.page_break_trigger:
            pdf.add_page()
            draw_itinerary_header(pdf)
            fill = True

        pdf.set_fill_color(*COLOR_FILA_ALTERNA) if fill else pdf.set_fill_color(*COLOR_BLANCO)
        fill = not fill
        start_x, start_y = pdf.get_x(), pdf.get_y()
        pdf.cell(sum(col_widths_it), row_height, "", border=1, fill=True)
        pdf.set_draw_color(*COLOR_LINEA)
        pdf.line(start_x + col_widths_it[0], start_y, start_x + col_widths_it[0], start_y + row_height)
        v_padding_day = (row_height - (len(lines_day) * line_height_it)) / 2
        pdf.set_xy(start_x, start_y + v_padding_day)
        pdf.set_font(FONT_CUERPO, 'B', 10)
        pdf.multi_cell(w=col_widths_it[0], h=line_height_it, text=day_text, align='C')
        pdf.set_xy(start_x + col_widths_it[0] + 3, start_y + 3)
        pdf.set_font(FONT_CUERPO, '', 10)
        pdf.multi_cell(w=col_widths_it[1] - 6, h=line_height_it, text=desc_text, align='L')
        pdf.set_y(start_y + row_height)

    pdf.ln(12)

    pdf.set_font(FONT_TITULOS, 'B', 14)
    pdf.cell(0, 10, "Precio del Paquete", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(3)
    pdf.set_font(FONT_CUERPO, 'B', 11)
    pdf.set_fill_color(*COLOR_FONDO_CABECERA)
    pdf.cell(63, 11, "Concepto", border=1, fill=True, align='C')
    pdf.cell(63, 11, "Cantidad", border=1, fill=True, align='C')
    pdf.cell(64, 11, "Total", border=1, fill=True, align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font(FONT_CUERPO, '', 11)
    cell_height_price = 12
    total_adultos = data["num_adultos"] * data["precio_adulto"]
    total_niños = data["num_niños"] * data["precio_niño"]
    total = total_adultos + total_niños
    pdf.set_fill_color(*COLOR_BLANCO)
    pdf.cell(63, cell_height_price, "Adulto(s)", border=1, fill=True, align='L')
    pdf.cell(63, cell_height_price, f"{data['num_adultos']} x {data['precio_adulto']:.2f} €", border=1, fill=True, align='C')
    pdf.cell(64, cell_height_price, f"{total_adultos:.2f} €", border=1, fill=True, align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    if data['num_niños'] > 0:
        pdf.set_fill_color(*COLOR_FILA_ALTERNA)
        pdf.cell(63, cell_height_price, "Niño(s)", border=1, fill=True, align='L')
        pdf.cell(63, cell_height_price, f"{data['num_niños']} x {data['precio_niño']:.2f} €", border=1, fill=True, align='C')
        pdf.cell(64, cell_height_price, f"{total_niños:.2f} €", border=1, fill=True, align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font(FONT_CUERPO, 'B', 12)
    pdf.set_fill_color(*COLOR_TOTAL)
    pdf.cell(126, cell_height_price, "TOTAL", border=1, fill=True, align='R')
    pdf.cell(64, cell_height_price, f"{total:.2f} €", border=1, fill=True, align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    if data["incluye"]:
        pdf.ln(12)
        pdf.set_font(FONT_TITULOS, 'B', 14)
        pdf.cell(0, 10, "Servicios Incluidos", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(3)
        for item in data["incluye"]:
            pdf.set_font("DejaVu", '', 11)
            pdf.set_text_color(*COLOR_CHECKMARK)
            pdf.write(pdf.font_size, "✓ ")
            pdf.set_text_color(*COLOR_TEXTO_PRINCIPAL)
            pdf.set_font(FONT_CUERPO, '', 11)
            pdf.multi_cell(0, 8, item, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(15)
    pdf.set_font(FONT_CUERPO, 'I', 9)
    pdf.set_text_color(150, 135, 115)
    texto_nota = (
        "El presente presupuesto tiene una vigencia de 48 horas desde su fecha de emisión. "
        "Las tarifas y disponibilidad están sujetas a confirmación al momento de la reserva."
        "La política de cancelaciones y devoluciones puede ser consultada en https://safarikeniatours.es/reembolso_devoluciones/. "
        "Para formalizar la reserva, será necesaria la aceptación de dichos términos en nuestra web y el pago de una señal del 20%."
    )
    pdf.multi_cell(0, 5, texto_nota, align='C')

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
        pdf.output(temp.name)
        return temp.name

    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=30)
    
    try:
        pdf.add_font(FONT_TITULOS, "", os.path.join("fonts", "Cinzel-Regular.ttf"))
        pdf.add_font(FONT_TITULOS, "B", os.path.join("fonts", "Cinzel-Bold.ttf"))
        pdf.add_font(FONT_CUERPO, "", os.path.join("fonts", "Lato-Regular.ttf"))
        pdf.add_font(FONT_CUERPO, "B", os.path.join("fonts", "Lato-Bold.ttf"))
        pdf.add_font(FONT_CUERPO, "I", os.path.join("fonts", "Lato-Italic.ttf"))
        pdf.add_font("DejaVu", "", os.path.join("fonts", "DejaVuSans.ttf"))
    except RuntimeError as e:
        st.error(f"Error al cargar fuentes: {e}. Asegúrate de tener Cinzel, Lato y DejaVuSans en la carpeta 'fonts'.")
        return None

    pdf.set_text_color(*COLOR_TEXTO_PRINCIPAL)

    logo_circulo_path = os.path.join("fonts", "logo_circulo.png")
    logo_texto_path = os.path.join("fonts", "logo_texto.png")
    if os.path.exists(logo_circulo_path):
        pdf.image(logo_circulo_path, x=15, y=10, w=25)
    if os.path.exists(logo_texto_path):
        pdf.image(logo_texto_path, x=45, y=12, w=70)
    pdf.set_font(FONT_TITULOS, 'B', 18)
    pdf.ln(20)
    pdf.cell(0, 25, data["titulo"], new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

    pdf.set_font(FONT_CUERPO, '', 11)
    line_height_datos = 7
    pdf.cell(0, line_height_datos, f"Número de presupuesto: {data['numero_presupuesto']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, line_height_datos, f"Fecha de emisión: {data['fecha_emision']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, line_height_datos, f"Contacto: {data['contacto']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)
    fecha_fin = data["fecha_inicio"] + timedelta(days=data["num_dias"] - 1)
    pdf.cell(0, line_height_datos, f"Régimen de comidas: Pensión completa", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, line_height_datos, f"Fecha estimada del viaje: {data['fecha_inicio'].strftime('%d de %B de %Y')} al {fecha_fin.strftime('%d de %B de %Y')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(12)

    pdf.set_font(FONT_TITULOS, 'B', 14)
    pdf.cell(0, 10, "Itinerario del Viaje", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(3)
    
    draw_itinerary_header(pdf)
    
    col_widths_it = (35, 155)
    line_height_it = 6.5
    fill = True
    for dia in data["itinerario"]:
        day_text, desc_text = f"{dia['dia']}\n({dia['fecha']})", f"{dia['actividad']}\nNoche en: {dia['noche']}"
        pdf.set_font(FONT_CUERPO, 'B', 10)
        lines_day = pdf.multi_cell(w=col_widths_it[0], h=line_height_it, text=day_text, dry_run=True, output=MethodReturnValue.LINES)
        pdf.set_font(FONT_CUERPO, '', 10)
        lines_desc = pdf.multi_cell(w=col_widths_it[1], h=line_height_it, text=desc_text, dry_run=True, output=MethodReturnValue.LINES)
        row_height = max(len(lines_day), len(lines_desc)) * line_height_it + 6
        
        if pdf.get_y() + row_height > pdf.page_break_trigger:
            pdf.add_page()
            draw_itinerary_header(pdf)
            fill = True

        pdf.set_fill_color(*COLOR_FILA_ALTERNA) if fill else pdf.set_fill_color(*COLOR_BLANCO)
        fill = not fill
        start_x, start_y = pdf.get_x(), pdf.get_y()
        pdf.cell(sum(col_widths_it), row_height, "", border=1, fill=True)
        pdf.set_draw_color(*COLOR_LINEA)
        pdf.line(start_x + col_widths_it[0], start_y, start_x + col_widths_it[0], start_y + row_height)
        v_padding_day = (row_height - (len(lines_day) * line_height_it)) / 2
        pdf.set_xy(start_x, start_y + v_padding_day)
        pdf.set_font(FONT_CUERPO, 'B', 10)
        pdf.multi_cell(w=col_widths_it[0], h=line_height_it, text=day_text, align='C')
        pdf.set_xy(start_x + col_widths_it[0] + 3, start_y + 3)
        pdf.set_font(FONT_CUERPO, '', 10)
        pdf.multi_cell(w=col_widths_it[1] - 6, h=line_height_it, text=desc_text, align='L')
        pdf.set_y(start_y + row_height)

    pdf.ln(12)
    
    pdf.set_font(FONT_TITULOS, 'B', 14)
    pdf.cell(0, 10, "Precio del Paquete", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(3)
    pdf.set_font(FONT_CUERPO, 'B', 11)
    pdf.set_fill_color(*COLOR_FONDO_CABECERA)
    pdf.cell(63, 11, "Concepto", border=1, fill=True, align='C')
    pdf.cell(63, 11, "Cantidad", border=1, fill=True, align='C')
    pdf.cell(64, 11, "Total", border=1, fill=True, align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font(FONT_CUERPO, '', 11)
    cell_height_price = 12
    total_adultos = data["num_adultos"] * data["precio_adulto"]
    total_niños = data["num_niños"] * data["precio_niño"]
    total = total_adultos + total_niños
    pdf.set_fill_color(*COLOR_BLANCO)
    pdf.cell(63, cell_height_price, "Adulto(s)", border=1, fill=True, align='L')
    pdf.cell(63, cell_height_price, f"{data['num_adultos']} x {data['precio_adulto']:.2f} €", border=1, fill=True, align='C')
    pdf.cell(64, cell_height_price, f"{total_adultos:.2f} €", border=1, fill=True, align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    if data['num_niños'] > 0:
        pdf.set_fill_color(*COLOR_FILA_ALTERNA)
        pdf.cell(63, cell_height_price, "Niño(s)", border=1, fill=True, align='L')
        pdf.cell(63, cell_height_price, f"{data['num_niños']} x {data['precio_niño']:.2f} €", border=1, fill=True, align='C')
        pdf.cell(64, cell_height_price, f"{total_niños:.2f} €", border=1, fill=True, align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font(FONT_CUERPO, 'B', 12)
    pdf.set_fill_color(*COLOR_TOTAL)
    pdf.cell(126, cell_height_price, "TOTAL", border=1, fill=True, align='R')
    pdf.cell(64, cell_height_price, f"{total:.2f} €", border=1, fill=True, align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    if data["incluye"]:
        pdf.ln(12)
        pdf.set_font(FONT_TITULOS, 'B', 14)
        pdf.cell(0, 10, "Servicios Incluidos", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(3)
        for item in data["incluye"]:
            pdf.set_font("DejaVu", '', 11)
            pdf.set_text_color(*COLOR_CHECKMARK)
            pdf.write(pdf.font_size, "✓ ")
            pdf.set_text_color(*COLOR_TEXTO_PRINCIPAL)
            pdf.set_font(FONT_CUERPO, '', 11)
            pdf.multi_cell(0, 8, item, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(15) 
    pdf.set_font(FONT_CUERPO, 'I', 9)
    pdf.set_text_color(150, 135, 115)
    texto_nota = (
        "El presente presupuesto tiene una vigencia de 48 horas desde su fecha de emisión. "
        "Las tarifas y disponibilidad están sujetas a confirmación al momento de la reserva."
        "La política de cancelaciones y devoluciones puede ser consultada en https://safarikeniatours.es/reembolso_devoluciones/"
        "Para formalizar la reserva, será necesaria la aceptación de dichos términos en nuestra web y el pago de una señal del 20%."
    )
    pdf.multi_cell(0, 5, texto_nota, align='C')

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
        pdf.output(temp.name)
        return temp.name

# --- INTERFAZ STREAMLIT CON PLANTILLAS REORGANIZADAS ---

st.title("🦒 Kenia Tours: Aplicación de presupuestos")
if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
    autenticar_usuario()
    st.stop()
if 'numero_presupuesto' not in st.session_state:
    st.session_state.numero_presupuesto = generar_num_presupuesto()

titulo = st.text_input("Título del presupuesto", value="Presupuesto Safari Personalizado")
st.markdown(f"**Número de presupuesto generado:** `{st.session_state.numero_presupuesto}`")

col1, col2 = st.columns(2)
with col1:
    fecha_emision = st.date_input("Fecha de emisión", value=datetime.today())
with col2:
    contacto = st.text_input("Contacto", value="+34 xxx xx xx xx")

fecha_inicio = st.date_input("Fecha de inicio del safari", value=datetime.today() + timedelta(days=30))
num_dias = st.number_input("Número de días del safari", min_value=1, value=2)

st.markdown("### 🗓️ Itinerario diario")
itinerario = []
for i in range(num_dias):
    fecha_dia = fecha_inicio + timedelta(days=i)
    st.markdown(f"--- \n**Día {i+1} ({fecha_dia.strftime('%d %b %Y')})**")
    
    # Selector de plantilla de actividad
    plantilla_act_sel = st.selectbox(
        "Plantilla de Actividad", 
        PLANTILLAS_ACTIVIDADES, 
        key=f"sb_act_{i}"
    )
    actividad_valor_inicial = "" if plantilla_act_sel == PLANTILLAS_ACTIVIDADES[0] else plantilla_act_sel
    actividad = st.text_area(f"Descripción de la Actividad", key=f"actividad_{i}", height=100, value=actividad_valor_inicial)
    
    # Selector de plantilla de hotel con formato para deshabilitar cabeceras
    def format_func(option):
        if option.startswith("---"):
            return f"--- {option.strip('- ')} ---"
        return f"   {option}"

    plantilla_noche_sel = st.selectbox(
        "Plantilla de Alojamiento", 
        PLANTILLAS_HOTELES_FLAT, 
        key=f"sb_noche_{i}",
        format_func=lambda x: x.strip() # Muestra el texto sin espacios extra
    )
    
    # Lógica para manejar la selección: si no es una cabecera, úsala.
    if plantilla_noche_sel.startswith("---"):
         noche_valor_inicial = ""
    else:
        noche_valor_inicial = plantilla_noche_sel

    noche = st.text_input(f"Noche en", key=f"noche_{i}", value=noche_valor_inicial)
    
    itinerario.append({"dia": i+1, "fecha": fecha_dia.strftime("%d %b %Y"), "actividad": actividad, "noche": noche})

st.markdown("---")
st.markdown("### 💶 Precios")
col1, col2 = st.columns(2)
with col1:
    num_adultos = st.number_input("Número de adultos", min_value=0, value=2)
    num_niños = st.number_input("Número de niños", min_value=0, value=0)
with col2:
    precio_adulto = st.number_input("Precio por adulto (€)", min_value=0.0, value=0.0, format="%.2f")
    precio_niño = st.number_input("Precio por niño (€)", min_value=0.0, value=0.0, format="%.2f")

st.markdown("### ✅ Servicios incluidos")
st.markdown("#### Selecciona los servicios estándar:")
incluye_default = [
    "Safari privado en 4x4 descapotable con guía en español.",
    "Pensión completa durante todo el recorrido.",
    "Agua embotellada ilimitada durante el safari.",
    "Alojamiento según itinerario.",
    "Todas las entradas a los parques y reservas nacionales.",
    "Traslados desde y hacia el aeropuerto internacional Jomo Kenyatta (Nairobi).",
    "Visita cultural a un poblado Masái (opcional, entrada incluida)."
]
servicios_seleccionados = []
for item in incluye_default:
    if st.checkbox(item, value=True, key=item):
        servicios_seleccionados.append(item)

st.markdown("#### Añadir servicios adicionales (uno por línea):")
servicios_adicionales = st.text_area(" ", label_visibility="collapsed", key="servicios_adicionales")

if st.button("📄 Generar presupuesto en PDF"):
    lista_final_incluye = servicios_seleccionados
    adicionales = [line.strip() for line in servicios_adicionales.split("\n") if line.strip()]
    lista_final_incluye.extend(adicionales)
    
    datos = {
        "titulo": titulo,
        "numero_presupuesto": st.session_state.numero_presupuesto,
        "fecha_emision": fecha_emision.strftime("%d de %B de %Y"),
        "contacto": contacto,
        "fecha_inicio": fecha_inicio,
        "num_dias": num_dias,
        "itinerario": itinerario,
        "num_adultos": num_adultos,
        "precio_adulto": precio_adulto,
        "num_niños": num_niños,
        "precio_niño": precio_niño,
        "incluye": lista_final_incluye
    }
    with st.spinner("Generando PDF..."):
        pdf_path = generar_pdf(datos)
        if pdf_path:
            with open(pdf_path, "rb") as f:
                st.download_button(
                    "⬇️ Descargar presupuesto",
                    data=f,
                    file_name=f"presupuesto_{datos['numero_presupuesto']}.pdf",
                    mime="application/pdf"
                )
            os.remove(pdf_path)