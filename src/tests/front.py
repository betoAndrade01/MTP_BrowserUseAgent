import streamlit as st
import subprocess
import os
from fpdf import FPDF
from pathlib import Path

# Deshabilitar advertencias
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Título y descripción
st.title("Cambio de Task para el Agente")
st.write("""
    En este panel, puedes ingresar un nuevo `task` para el agente y ejecutarlo.
    El task será enviado al agente y se procesará.
""")

# Campo de texto para ingresar el nuevo task
task_input = st.text_area(
    "Ingrese el Task:", 
    value="Importante: Eres un experto en automatización de pruebas...",
    height=150
)

# Función para generar el PDF
def generate_pdf_from_screenshots(folder_path: str, output_pdf_path: str):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    screenshot_folder = Path(folder_path).resolve()
    screenshot_files = sorted(screenshot_folder.glob("*.png"))

    if not screenshot_files:
        raise ValueError("No se encontraron capturas de pantalla para generar el PDF.")

    for screenshot in screenshot_files:
        pdf.add_page()
        pdf.image(str(screenshot), x=10, y=10, w=190)  # Ajusta el tamaño si es necesario

    pdf.output(output_pdf_path)
    return output_pdf_path

# Botón para ejecutar el task
if st.button("Ejecutar Task"):
    if task_input.strip() == "":
        st.warning("Por favor, ingrese un task válido.")
    else:
        try:
            # Ejecutamos el agente con el nuevo task
            result = subprocess.run(
                ["python", "src/tests/agent_front.py", task_input],
                capture_output=True, text=True
            )
            # Mostrar la salida del proceso
            st.write("Resultado de la ejecución:")
            st.text(result.stdout)  # Mostramos el resultado en la interfaz
            if result.stderr:
                st.error(f"Error: {result.stderr}")
            
            # Habilitar el botón "Generar PDF" después de la ejecución
            screenshot_folder = "src/tests/capturas"  # Ruta donde se guardan las capturas
            if os.path.exists(screenshot_folder) and len(os.listdir(screenshot_folder)) > 0:
                st.success("Task ejecutado correctamente. Ahora puedes generar el PDF.")
                
                if st.button("Generar PDF"):
                    try:
                        output_pdf_path = "src/tests/output.pdf"
                        pdf_file_path = generate_pdf_from_screenshots("src/tests/capturas", output_pdf_path)

                        with open(pdf_file_path, "rb") as f:
                            st.download_button(
                                label="Descargar PDF",
                                data=f,
                                file_name="capturas.pdf",
                                mime="application/pdf"
                            )
                    except Exception as e:
                        st.error(f"Error al generar el PDF: {e}")

        except Exception as e:
            st.error(f"Hubo un error al ejecutar el task: {e}")
