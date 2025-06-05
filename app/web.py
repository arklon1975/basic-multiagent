from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
from pathlib import Path
import asyncio
from typing import List, Dict
import json

from .multiagent import multiagent
from .logger import logger

app = FastAPI(title="Sistema Multi-Agente de Marketing")

# Configurar templates y archivos estáticos
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Almacenar resultados de las ejecuciones
execution_results: Dict[str, List[Dict]] = {}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Página principal de la aplicación."""
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.post("/execute")
async def execute_task(prompt: str = Form(...)):
    """Ejecuta una tarea en el sistema multi-agente."""
    try:
        # Generar un ID único para esta ejecución
        execution_id = str(len(execution_results))
        execution_results[execution_id] = []
        
        # Ejecutar el sistema multi-agente
        for s in multiagent.stream(
            {
                "messages": [
                    HumanMessage(content=prompt)
                ],
            },
            {"recursion_limit": 150}
        ):
            if not "__end__" in s:
                execution_results[execution_id].append(s)
                logger.info(f"Progreso de ejecución {execution_id}: {s}")
        
        return {"status": "success", "execution_id": execution_id}
    except Exception as e:
        logger.error(f"Error en la ejecución: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.get("/results/{execution_id}")
async def get_results(execution_id: str):
    """Obtiene los resultados de una ejecución específica."""
    if execution_id not in execution_results:
        return {"status": "error", "message": "Ejecución no encontrada"}
    
    return {
        "status": "success",
        "results": execution_results[execution_id]
    }

def start():
    """Inicia el servidor web."""
    uvicorn.run(
        "app.web:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 