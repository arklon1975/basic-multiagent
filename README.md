# Sistema Multi-Agente de Marketing de Contenidos

Este proyecto implementa un sistema multi-agente para la gestión de contenido de marketing, utilizando LangChain y OpenAI.

## Requisitos

- Python 3.11 o superior
- Poetry para gestión de dependencias
- API key de OpenAI
- API key de Tavily (opcional, para búsquedas web)

## Instalación

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd basicmultiagent
```

2. Instalar dependencias con Poetry:
```bash
poetry install
```

3. Configurar variables de entorno:
Crear un archivo `.env` en la raíz del proyecto con:
```
OPENAI_API_KEY=tu-api-key-de-openai
OPENAI_MODEL_NAME=gpt-4-turbo-preview  # opcional, por defecto usa gpt-4-turbo-preview
TAVILY_API_KEY=tu-api-key-de-tavily  # opcional
```

## Uso

### Interfaz Web

Para iniciar la interfaz web:

```bash
poetry run python run.py
```

Luego, abre tu navegador y visita:
```
http://localhost:8000
```

La interfaz web te permite:
- Ingresar prompts para el sistema multi-agente
- Ver los resultados en tiempo real
- Seguir el progreso de la ejecución

### Uso por Línea de Comandos

Para ejecutar el sistema multi-agente directamente:

```bash
poetry run python -m app.multiagent
```

## Estructura del Proyecto

- `app/multiagent.py`: Implementación principal del sistema multi-agente
- `app/web.py`: Servidor web FastAPI
- `app/templates/`: Plantillas HTML
- `app/static/`: Archivos estáticos
- `tests/`: Directorio para pruebas unitarias
- `pyproject.toml`: Configuración del proyecto y dependencias

## Agentes

El sistema incluye tres tipos de agentes:

1. **Investigador Online**: Busca y recopila información relevante
2. **Gestor de Blog**: Optimiza y mejora el contenido para blogs
3. **Gestor de Redes Sociales**: Adapta el contenido para redes sociales

## Características

- Interfaz web moderna y responsiva
- Sistema de logging con rotación de archivos
- Rate limiting para llamadas a APIs
- Sistema de caché para optimizar rendimiento
- Validación de entrada y sanitización
- Pruebas unitarias

## Licencia

MIT
