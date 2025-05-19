# Excel Chainlit

Aplicación interactiva para analizar archivos Excel utilizando PandasAI y OpenAI, con una interfaz de chat construida con Chainlit.

## Características

- 📊 Análisis de archivos Excel usando procesamiento de lenguaje natural
- 🤖 Integración con OpenAI para generar análisis inteligentes
- 📈 Generación y visualización de gráficos
- 💬 Interfaz de chat intuitiva para consultas en lenguaje natural
- 🔄 Ejecución de herramientas como listar archivos, ver metadatos y analizar datos

## Tecnologías

- **Backend**: Python, OpenAI Agents SDK
- **Análisis de datos**: PandasAI, Pandas
- **Interfaz**: Chainlit
- **Integración AI**: OpenAI GPT-4o

## Instalación

### Requisitos previos

- Python 3.9+
- Una API key de OpenAI

### Configuración

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/excel-chainlit.git
cd excel-chainlit
```

2. Crear un entorno virtual:
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar la API key de OpenAI:
```bash
echo "OPENAI_API_KEY=tu-api-key" > .env
```

## Uso

1. Coloca tus archivos Excel en el directorio `data/`

2. Inicia la aplicación:
```bash
chainlit run app/chainlit_app.py
```

3. Abre tu navegador en `http://localhost:8000`

## Ejemplos de consultas

- "¿Qué archivos Excel hay disponibles?"
- "¿Puedes mostrarme la metadata de los archivos Excel?"
- "Analiza ejemplo1.xlsx y dime cuáles son los valores máximos"
- "Genera un gráfico de barras con los datos de ventas.xlsx"

## Estructura del proyecto

```
excel-chainlit/
├── app/                    # Código principal de la aplicación
│   ├── agent_setup.py     # Configuración del agente de OpenAI
│   └── chainlit_app.py    # Aplicación Chainlit
├── data/                   # Directorio para archivos Excel
├── exports/                # Directorio para exportar gráficos y resultados
├── tools/                  # Herramientas personalizadas
│   └── pandasai_tool.py   # Integración con PandasAI
└── utils/                  # Utilidades y funciones auxiliares
    └── file_manager.py    # Gestión de archivos
```

## Licencia

MIT

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue para discutir cambios importantes antes de enviar un PR.