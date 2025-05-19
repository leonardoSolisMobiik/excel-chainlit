import os
import re
import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm import OpenAI
from langchain.tools import BaseTool
from typing import Any, ClassVar

class AnalizarYGuardarExcelTool(BaseTool):
    name: ClassVar[str] = "analizar_y_guardar_excel"
    description: ClassVar[str] = (
        "Analiza un archivo Excel usando PandasAI y guarda el resultado en un nuevo archivo Excel. "
        "Uso: '<archivo_entrada.xlsx>: <instrucción>; guardar como <archivo_salida.xlsx>'. "
        "Si no se especifica el nombre de salida, el asistente debe pedirlo."
    )

    def _run(self, query: str, **kwargs) -> Any:
        """
        Espera un string con formato: '<archivo_entrada.xlsx>: <instrucción>; guardar como <archivo_salida.xlsx>'
        """
        # Extraer archivo de entrada, instrucción y archivo de salida
        match = re.match(r"(.+\.xlsx|.+\.xls)\s*:\s*(.+?)(?:;\s*guardar como\s*(.+\.xlsx|.+\.xls))?$", query, re.IGNORECASE)
        if not match:
            return ("[Error] Formato incorrecto. Usa: <archivo_entrada.xlsx>: <instrucción>; guardar como <archivo_salida.xlsx> "
                    "(o especifica el nombre de salida cuando se te pida).")
        file_name = match.group(1).strip()
        instruction = match.group(2).strip()
        output_file = match.group(3).strip() if match.group(3) else None
        file_path = os.path.join("data", file_name)
        if not os.path.exists(file_path):
            return f"[Error] El archivo '{file_path}' no existe."
        if not output_file:
            return ("¿Con qué nombre quieres guardar el archivo de resultado? "
                    "Por favor, responde con el nombre deseado (ejemplo: resultado.xlsx)")
        try:
            df = pd.read_excel(file_path)
        except Exception as e:
            return f"[Error] No se pudo leer el archivo Excel: {e}"
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return "[Error] No se encontró ninguna API key de OpenAI en las variables de entorno."
            llm = OpenAI(api_token=api_key)
            sdf = SmartDataframe(df, config={"llm": llm})
            result = sdf.chat(instruction)
            if isinstance(result, pd.DataFrame):
                output_path = os.path.join("data", output_file)
                result.to_excel(output_path, index=False)
                preview = result.head(5).to_string(index=False)
                return (f"Resultado guardado en /data/{output_file}.\nPreview de los primeros registros:\n{preview}")
            else:
                return ("El resultado del análisis no es una tabla de datos (DataFrame), por lo que no se puede guardar en Excel. "
                        f"Resultado obtenido: {str(result)}")
        except Exception as e:
            return f"[Error] PandasAI falló: {e}"

    def _arun(self, query: str, **kwargs) -> Any:
        raise NotImplementedError("Esta herramienta no soporta ejecución asíncrona todavía.") 