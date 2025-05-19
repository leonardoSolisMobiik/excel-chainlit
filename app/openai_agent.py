import os
from openai import OpenAI
from tools.pandasai_tool import PandasAITool
from utils.file_manager import list_excel_files, get_excel_files_metadata
import json
import time
import asyncio

# Inicializar cliente de OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Definir herramientas
tools = [
    {
        "type": "function",
        "function": {
            "name": "listar_archivos_excel",
            "description": "Lista todos los archivos Excel disponibles en la carpeta /data.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "metadata_archivos_excel",
            "description": "Devuelve la metadata de los archivos Excel en la carpeta /data.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analizar_excel",
            "description": "Analiza un archivo Excel usando PandasAI.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Nombre del archivo Excel en la carpeta /data (ej. 'ejemplo1.xlsx')"
                    },
                    "query": {
                        "type": "string",
                        "description": "Pregunta o instrucción para analizar el archivo"
                    }
                },
                "required": ["filename", "query"]
            }
        }
    }
]

# Funciones para ejecutar herramientas
def execute_tool(tool_name, arguments=None):
    """Ejecuta la herramienta especificada con los argumentos dados."""
    if arguments is None:
        arguments = {}
    
    if tool_name == "listar_archivos_excel":
        files = list_excel_files()
        if files:
            return "Archivos Excel disponibles: " + ", ".join(files)
        return "No se encontraron archivos Excel en la carpeta /data."
    
    elif tool_name == "metadata_archivos_excel":
        metadata = get_excel_files_metadata()
        if metadata:
            msg = "Metadata de archivos Excel:\n"
            for m in metadata:
                msg += f"- {m['nombre']} | {m['tamano_bytes']} bytes | Última modificación: {m['ultima_modificacion']}\n"
            return msg
        return "No se encontró metadata de archivos Excel en la carpeta /data."
    
    elif tool_name == "analizar_excel":
        filename = arguments.get("filename")
        query = arguments.get("query")
        
        if not filename or not query:
            return "Error: Se requiere el nombre del archivo y la consulta."
        
        # Usar PandasAITool
        tool = PandasAITool()
        return tool._run(f"{filename}: {query}")
    
    else:
        return f"Error: Herramienta '{tool_name}' no reconocida."

# Clase de agente con simulación de streaming
class AssistantAgent:
    def __init__(self, assistant_id=None):
        self.client = client
        
        # Intentar recuperar un asistente existente o crear uno nuevo
        if assistant_id:
            try:
                self.assistant = client.beta.assistants.retrieve(assistant_id)
                print(f"Usando asistente existente: {self.assistant.id}")
            except Exception as e:
                print(f"Error al recuperar asistente: {e}. Creando nuevo...")
                self.assistant = self._create_assistant()
        else:
            # Crear asistente
            self.assistant = self._create_assistant()
            print(f"Nuevo asistente creado: {self.assistant.id}")
    
    def _create_assistant(self):
        """Crea un nuevo asistente con las herramientas configuradas."""
        return client.beta.assistants.create(
            name="Excel Analyzer",
            instructions="Eres un asistente experto en análisis de datos de Excel. SIEMPRE usa las herramientas disponibles cuando sea apropiado. Usa 'listar_archivos_excel' antes de analizar cualquier archivo.",
            tools=tools,
            model="gpt-4o"
        )
    
    async def arun(self, query):
        # Crear un thread
        thread = self.client.beta.threads.create()
        
        # Agregar mensaje del usuario al thread
        self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=query
        )
        
        # Ejecutar el asistente en el thread
        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self.assistant.id
        )
        
        # Inicializar variables para tracking de tokens
        last_content = ""
        assistant_message_id = None
        
        # Polling para simular streaming
        while True:
            # Obtener estado actual de la ejecución
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            
            # Manejar estado "requires_action" (llamada a herramienta)
            if run.status == "requires_action":
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []
                
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    # Mostrar información de la herramienta
                    yield f"\n\n[Ejecutando herramienta: {function_name}]\n"
                    
                    # Ejecutar la herramienta
                    result = execute_tool(function_name, arguments)
                    
                    # Mostrar el resultado
                    yield f"{result}\n\n"
                    
                    # Agregar a las salidas de herramientas
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": result
                    })
                
                # Enviar resultados al asistente
                self.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
            
            # Si la ejecución está en progreso o completa, buscar mensajes nuevos/actualizados
            elif run.status in ["in_progress", "completed"]:
                # Obtener mensajes, ordenados por más reciente primero
                messages = self.client.beta.threads.messages.list(
                    thread_id=thread.id,
                    order="desc",
                    limit=1  # Solo el mensaje más reciente
                )
                
                # Buscar el mensaje más reciente del asistente
                for msg in messages.data:
                    if msg.role == "assistant":
                        # Si es un mensaje nuevo o el mismo mensaje con contenido actualizado
                        if (assistant_message_id is None or 
                            msg.id == assistant_message_id):
                            
                            # Actualizar ID del mensaje actual
                            assistant_message_id = msg.id
                            
                            # Obtener todo el contenido de texto del mensaje
                            full_content = ""
                            for content_part in msg.content:
                                if content_part.type == "text":
                                    full_content += content_part.text.value
                            
                            # Si hay nuevo contenido
                            if full_content != last_content:
                                # Solo enviar la parte nueva
                                new_content = full_content[len(last_content):]
                                if new_content:
                                    yield new_content
                                
                                # Actualizar último contenido visto
                                last_content = full_content
                        
                        break  # Solo procesamos el primer mensaje
            
            # Si la ejecución ha terminado y ya enviamos todo el contenido, salimos
            if run.status == "completed" and assistant_message_id is not None:
                break
            
            # Si ocurrió un error
            if run.status in ["failed", "cancelled", "expired"]:
                yield f"\n\nError: La ejecución finalizó con estado {run.status}.\n"
                break
            
            # Pausa breve para no sobrecargar la API
            await asyncio.sleep(0.3)

# Instanciar agente (usar ID existente si está disponible)
assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
agent_graph = AssistantAgent(assistant_id)