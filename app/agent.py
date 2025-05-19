from langchain.agents import initialize_agent, AgentType, Tool
from langchain_openai import ChatOpenAI
from tools.pandasai_tool import PandasAITool
from utils.file_manager import list_excel_files, get_excel_files_metadata
import os

# --- Prompt de sistema personalizado para Aria ---
system_prompt = (
    "Eres Aria, la asistente virtual de la CNBV. "
    "Tu objetivo es ayudar a los usuarios a analizar archivos Excel y responder preguntas generales. "
    "- Si el usuario te pregunta sobre archivos Excel (listar, analizar, obtener metadata), utiliza las herramientas disponibles. "
    "- Si la pregunta es general, responde con tu conocimiento. "
    "- Siempre responde de manera profesional y clara, presentándote como Aria."
)

# --- Subtarea 4.1: Inicialización explícita del modelo GPT-4o ---
# Usa la API key de OpenAI y el modelo GPT-4o
llm = ChatOpenAI(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o",
    temperature=float(os.getenv("CHAT_TEMPERATURE", 0.0)),
    streaming=True,
)

# --- Herramientas para el agente ---
def tool_list_excels(_):
    files = list_excel_files()
    if files:
        return "Archivos Excel disponibles: " + ", ".join(files)
    return "No se encontraron archivos Excel en la carpeta /data."

def tool_metadata_excels(_):
    metadata = get_excel_files_metadata()
    if metadata:
        msg = "Metadata de archivos Excel:\n"
        for m in metadata:
            msg += f"- {m['nombre']} | {m['tamano_bytes']} bytes | Última modificación: {m['ultima_modificacion']}\n"
        return msg
    return "No se encontró metadata de archivos Excel en la carpeta /data."

# Registrar herramientas con nombres válidos para OpenAI
herramientas = [
    Tool(
        name="listar_archivos_excel",
        func=tool_list_excels,
        description="Lista todos los archivos Excel disponibles en la carpeta /data."
    ),
    Tool(
        name="metadata_archivos_excel",
        func=tool_metadata_excels,
        description="Devuelve la metadata de los archivos Excel en la carpeta /data."
    ),
    PandasAITool(),
]

# --- Inicialización del agente con AgentType.OPENAI_FUNCTIONS ---
agent = initialize_agent(
    tools=herramientas,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
    system_message=system_prompt,
    handle_parsing_errors=True,
)

def ask_excel_agent(file_name: str, instruction: str) -> str:
    """
    Envía una instrucción y un archivo Excel al agente para obtener una respuesta.
    """
    try:
        query = f"{file_name}: {instruction}"
        result = agent.run(query)
        return str(result)
    except Exception as e:
        return f"[Error agente] {e}"

def ask_aria_agent(message: str) -> str:
    """
    Envía cualquier mensaje al agente Aria y devuelve la respuesta.
    """
    try:
        result = agent.run(message)
        return str(result)
    except Exception as e:
        return f"[Error agente] {e}" 