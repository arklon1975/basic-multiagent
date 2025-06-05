# Sistema Multi-Agente de Marketing de Contenidos

Este proyecto implementa un sistema multi-agente para la automatización de tareas de marketing de contenidos, utilizando inteligencia artificial y herramientas de scraping, validación, caché y control de flujo. Permite la colaboración entre agentes especializados para investigar, redactar y difundir contenido de manera eficiente.

## Características principales
- **Multi-agente**: Coordinación entre agentes para investigación, redacción de blogs y gestión de redes sociales.
- **Interfaz web moderna**: Interacción sencilla y visualización de resultados en tiempo real.
- **Validación y seguridad**: Validación de entradas, manejo de errores y control de acceso a APIs.
- **Caché y rate limiting**: Optimización de recursos y protección contra abusos.
- **Registro de logs**: Seguimiento de operaciones y errores.
- **Extensible y modular**: Fácil de adaptar y ampliar con nuevos agentes o herramientas.

## Capturas de pantalla
A continuación se muestran ejemplos de la interfaz web:

### Pantalla principal
![Pantalla principal](docs/screenshots/home.png)

### Resultados de ejecución
![Resultados de ejecución](docs/screenshots/result.png)

> Guarda tus capturas en la carpeta `docs/screenshots/` con los nombres sugeridos o actualiza las rutas en el README.

## Requisitos
- Python 3.10+
- [Poetry](https://python-poetry.org/docs/#installation)
- Clave de API de OpenAI (y otras si se usan herramientas externas)

## Instalación
1. Clona el repositorio:
   ```bash
   git clone https://github.com/arklon1975/basic-multiagent.git
   cd basic-multiagent
   ```
2. Instala las dependencias:
   ```bash
   poetry install
   ```
3. Copia el archivo de ejemplo de variables de entorno y configura tu clave de OpenAI:
   ```bash
   cp .env.example .env
   # Edita .env y agrega tu OPENAI_API_KEY
   ```

## Configuración
- Edita el archivo `.env` para agregar tu clave de OpenAI y otros parámetros necesarios.
- Puedes modificar los agentes y sus prompts en `app/multiagent.py`.

## Uso
### Interfaz Web
1. Inicia el servidor web:
   ```bash
   poetry run python run.py
   ```
2. Abre tu navegador en [http://localhost:8000](http://localhost:8000)
3. Ingresa tu solicitud en el formulario y visualiza los resultados en tiempo real.

#### Ejemplo de uso en la web
- Escribe un prompt como: `Genera un artículo sobre tendencias de IA en 2024 y crea un tweet para difundirlo.`
- Haz clic en "Ejecutar" y observa cómo los agentes colaboran para generar el contenido.

### Línea de Comandos
También puedes ejecutar el sistema directamente desde la terminal modificando el bloque final de `app/multiagent.py` para pruebas rápidas.

#### Ejemplo de uso en terminal
```python
# En app/multiagent.py (bloque final)
for s in multiagent.stream(
    {
        "messages": [
            HumanMessage(
                content="Escribe un informe sobre el impacto de la IA en el marketing digital."
            )
        ],
    },
    {"recursion_limit": 150}
):
    if not "__end__" in s:
        print(s, end="\n\n-----------------\n\n")
```

## Estructura del Proyecto
```
├── app/
│   ├── cache.py           # Sistema de caché
│   ├── logger.py          # Registro de logs
│   ├── multiagent.py      # Lógica principal de los agentes
│   ├── rate_limiter.py    # Limitador de peticiones
│   ├── validators.py      # Validación y sanitización de entradas
│   ├── web.py             # Servidor web FastAPI
│   ├── templates/
│   │   └── index.html     # Plantilla HTML principal
│   └── static/            # Archivos estáticos (CSS, JS, imágenes)
├── docs/screenshots/      # Capturas de pantalla
├── tests/                 # Pruebas unitarias
├── logs/                  # Archivos de log
├── run.py                 # Script de arranque
├── pyproject.toml         # Configuración de dependencias
├── README.md              # Este archivo
└── .env.example           # Ejemplo de configuración de entorno
```

## Contribuciones
¡Las contribuciones son bienvenidas! Por favor, abre un issue o pull request para sugerencias, mejoras o corrección de errores.

## Licencia
Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.

## Contacto
Para dudas, sugerencias o soporte, puedes abrir un issue en el repositorio o contactar al autor principal.
