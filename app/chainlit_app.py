import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import chainlit as cl
from agents.run import Runner
from app.agent_setup import get_excel_agent
import asyncio

# Obtener el agente configurado
excel_agent = get_excel_agent()

@cl.on_message
async def on_message(message: cl.Message):
    # Tomar el contenido del mensaje
    user_query = message.content.strip()
    
    # --- MEMORIA DE SESIÓN ---
    # Recuperar historial de mensajes de la sesión del usuario
    history = cl.user_session.get("history", [])
    # Agregar el nuevo mensaje del usuario
    history.append({"role": "user", "content": user_query})
    
    # Limitar el historial a las últimas 20 interacciones
    MAX_HISTORY = 20
    history = history[-MAX_HISTORY:]
    
    # Mensaje de feedback opcional (puedes comentar si no lo quieres)
    # await cl.Message(content="Procesando consulta...", author="Excel Assistant").send()
    
    try:
        # Ejecutar el agente con el historial de mensajes (memoria)
        # NOTA: Si el agente no soporta historial, solo envía el último mensaje
        streamed_result = Runner.run_streamed(
            excel_agent,
            input=[{"role": h["role"], "content": h["content"]} for h in history]
        )
        full_response = ""

        # Crear mensaje para streaming en Chainlit
        msg = cl.Message(content="", author="Excel Assistant")
        await msg.send()

        async for event in streamed_result.stream_events():
            # Procesar eventos de streaming
            if hasattr(event, 'type'):
                if event.type == "run_item_stream_event":
                    # Mensaje del modelo o resultado de herramienta
                    item = event.item
                    if hasattr(item, 'type') and item.type == "message_output_item":
                        # Mensaje del modelo (token o bloque)
                        last_content = item.raw_item.content[-1]
                        if hasattr(last_content, 'text'):
                            token = last_content.text
                            if token:
                                full_response += token
                                await msg.stream_token(token)
                    elif hasattr(item, 'type') and item.type == "tool_call_output_item":
                        # Resultado de herramienta
                        output = getattr(item, 'output', None)
                        if output:
                            full_response += str(output)
                            await msg.stream_token(str(output))
                elif event.type == "raw_response_event":
                    data = getattr(event, 'data', None)
                    if data and hasattr(data, 'delta'):
                        print("[DEBUG] Delta recibido:", data.delta)
                        delta = data.delta
                        if delta and hasattr(delta, 'content'):
                            token = delta.content
                            if token:
                                full_response += token
                                await msg.stream_token(token)
                        elif isinstance(delta, str):
                            full_response += delta
                            await msg.stream_token(delta)
                # Puedes agregar más tipos de eventos si lo deseas

        # Actualizar mensaje final
        await msg.update()
        # Guardar la respuesta del asistente en el historial
        history.append({"role": "assistant", "content": full_response})
        cl.user_session.set("history", history)
        
    except Exception as e:
        # Manejar errores
        error_msg = f"Error al procesar la consulta: {str(e)}"
        # Al final, envía el error como un nuevo mensaje
        await cl.Message(content=error_msg, author="Excel Assistant").send()
        # Guardar el error en el historial
        history.append({"role": "assistant", "content": error_msg})
        cl.user_session.set("history", history)