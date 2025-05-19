import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import Optional, List, Dict, Any, Union
# Import correcto del paquete agents
from agents import Agent, function_tool
from tools.pandasai_tool import PandasAITool
from tools.guardar_excel_tool import AnalizarYGuardarExcelTool
from utils.file_manager import list_excel_files, get_excel_files_metadata

# --- Función de herramienta para listar archivos Excel ---
@function_tool
def listar_archivos_excel() -> str:
    """Lista todos los archivos Excel disponibles en la carpeta /data."""
    files = list_excel_files()
    if files:
        return "Archivos Excel disponibles: " + ", ".join(files)
    return "No se encontraron archivos Excel en la carpeta /data."

# --- Función de herramienta para mostrar metadata de archivos Excel ---
@function_tool
def metadata_archivos_excel() -> str:
    """Devuelve la metadata de los archivos Excel en la carpeta /data."""
    metadata = get_excel_files_metadata()
    if metadata:
        msg = "Metadata de archivos Excel:\n"
        for m in metadata:
            msg += f"- {m['nombre']} | {m['tamano_bytes']} bytes | Última modificación: {m['ultima_modificacion']}\n"
        return msg
    return "No se encontró metadata de archivos Excel en la carpeta /data."

# --- Función de herramienta para analizar archivos Excel con PandasAI ---
@function_tool
def analizar_excel(filename: str, query: str) -> str:
    """
    Analiza un archivo Excel usando PandasAI.
    
    Args:
        filename: Nombre del archivo Excel en la carpeta /data (ej. 'ejemplo1.xlsx')
        query: Pregunta o instrucción para analizar el archivo
    """
    tool = PandasAITool()
    return tool._run(f"{filename}: {query}")

# --- Herramienta para analizar y guardar resultado en Excel (como función) ---
@function_tool
def analizar_y_guardar_excel(filename: str, query: str, output_filename: str) -> str:
    """
    Analiza un archivo Excel usando PandasAI y guarda el resultado en un nuevo archivo Excel.
    """
    tool = AnalizarYGuardarExcelTool()
    query_str = f"{filename}: {query}; guardar como {output_filename}"
    return tool._run(query_str)

# --- Crear y configurar agente para análisis de Excel ---
excel_agent = Agent(
    name="Excel Analyzer",
    instructions="""
Eres Aria, un asistente experto en análisis de datos Excel y automatización de tareas de oficina.

**Reglas de comportamiento:**
- Siempre responde en español, de manera clara y profesional.
- Si el usuario pregunta por archivos, usa la herramienta `listar_archivos_excel`.
- Si el usuario pide detalles, usa `metadata_archivos_excel`.
- Si el usuario solicita un análisis, usa `analizar_excel` y explica el resultado de forma sencilla.
- Si el usuario solicita un análisis y que el resultado se guarde en un nuevo archivo, usa la herramienta `analizar_y_guardar_excel`.
- Si la consulta no es sobre Excel, responde amablemente que solo puedes ayudar con análisis de archivos Excel.
- Si usas una herramienta, explica brevemente qué hiciste y muestra el resultado.
- Si ocurre un error, informa al usuario de forma empática y sugiere cómo corregirlo.

**Formato de respuesta:**
- Responde primero con un resumen breve.
- Si hay pasos, enuméralos.
- Muestra el resultado final en negritas o con formato claro.

**Ejemplo de respuesta:**
Usuario: ¿Cuál es el promedio de la columna A en ejemplo1.xlsx?
Aria:
1. He analizado el archivo `ejemplo1.xlsx` usando PandasAI.
2. El promedio de la columna A es **2.5**.

Usuario: ventas_globales.xlsx: filtra las ventas de Europa; guardar como ventas_europa.xlsx
Aria:
1. He filtrado las ventas de Europa y guardado el resultado en `/data/ventas_europa.xlsx`.
2. Aquí tienes una vista previa de los primeros registros.

¿Te gustaría realizar otro análisis o ver la lista de archivos disponibles?
""",
    tools=[listar_archivos_excel, metadata_archivos_excel, analizar_excel, analizar_y_guardar_excel],
    model="gpt-4o"
)

# Función para acceder al agente configurado
def get_excel_agent():
    return excel_agent