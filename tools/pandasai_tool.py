from langchain.tools import BaseTool
from typing import Optional, Any, ClassVar
import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm import OpenAI
import os
import re

class PandasAITool(BaseTool):
    name: ClassVar[str] = "pandasai_tool"
    description: ClassVar[str] = (
        "Herramienta para analizar archivos Excel usando PandasAI. "
        "Uso: '<archivo.xlsx>: <instrucción en lenguaje natural>'."
    )

    def _run(self, query: str, **kwargs) -> Any:
        """
        Espera un string con formato: '<archivo.xlsx>: <instrucción>'
        """
        # Extraer archivo e instrucción
        match = re.match(r"(.+\.xlsx|.+\.xls)\s*:\s*(.+)", query)
        if not match:
            return "[Error] Formato incorrecto. Usa: <archivo.xlsx>: <instrucción>"
        file_name = match.group(1).strip()
        instruction = match.group(2).strip()
        file_path = os.path.join("data", file_name)
        if not os.path.exists(file_path):
            return f"[Error] El archivo '{file_path}' no existe."
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
            # Si el resultado es un DataFrame, conviértelo a string
            if isinstance(result, pd.DataFrame):
                return result.to_string(index=False)
            return result
        except Exception as e:
            return f"[Error] PandasAI falló: {e}"

    def _arun(self, query: str, **kwargs) -> Any:
        raise NotImplementedError("PandasAITool no soporta ejecución asíncrona todavía.") 