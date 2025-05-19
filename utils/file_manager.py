import os
import time
from typing import List, Dict, Optional

EXCEL_EXTENSIONS = ('.xlsx', '.xls')

class MemoryBank:
    """
    Simple memory bank para cachear resultados de funciones de archivos Excel.
    """
    def __init__(self, ttl: int = 10):
        self.ttl = ttl  # tiempo de vida en segundos
        self._cache = {}
        self._timestamps = {}

    def get(self, key: str) -> Optional[object]:
        if key in self._cache and (time.time() - self._timestamps[key] < self.ttl):
            return self._cache[key]
        return None

    def set(self, key: str, value: object):
        self._cache[key] = value
        self._timestamps[key] = time.time()

memory_bank = MemoryBank(ttl=10)

def list_excel_files(data_dir: str = "data") -> List[str]:
    """
    Lista todos los archivos Excel en el directorio especificado.
    """
    cache_key = f"list_excel_files:{data_dir}"
    cached = memory_bank.get(cache_key)
    if cached is not None:
        return cached
    if not os.path.exists(data_dir):
        return []
    files = [f for f in os.listdir(data_dir)
             if f.lower().endswith(EXCEL_EXTENSIONS) and os.path.isfile(os.path.join(data_dir, f))]
    memory_bank.set(cache_key, files)
    return files

def get_excel_files_metadata(data_dir: str = "data") -> List[Dict]:
    """
    Devuelve una lista de diccionarios con metadata de los archivos Excel en el directorio.
    Cada diccionario contiene: nombre, tamaño (bytes), fecha de última modificación (ISO).
    """
    cache_key = f"get_excel_files_metadata:{data_dir}"
    cached = memory_bank.get(cache_key)
    if cached is not None:
        return cached
    files = list_excel_files(data_dir)
    metadata = []
    for f in files:
        path = os.path.join(data_dir, f)
        try:
            stat = os.stat(path)
            metadata.append({
                "nombre": f,
                "tamano_bytes": stat.st_size,
                "ultima_modificacion":  os.path.getmtime(path)
            })
        except Exception as e:
            # Si hay error, lo ignoramos para este archivo
            continue
    memory_bank.set(cache_key, metadata)
    return metadata 