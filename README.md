# ms-notifications (FastAPI + MongoDB)

## Requisitos
- Python 3.10+
- MongoDB disponible (local o remoto)

## Configuración
Copia el archivo `.env.example` a `.env` y ajusta valores.

## Ejecutar
Instala dependencias:

```bash
pip install -r requirements.txt
```

Ejecuta el servidor:

```bash
uvicorn app.main:app --app-dir src --reload --host 0.0.0.0 --port 8000
```

## OpenAPI/Swagger
- Swagger UI: `http://localhost:8083/docs`
- OpenAPI JSON: `http://localhost:8083/openapi.json`

## Endpoints
- `GET /notifications`
- `GET /notifications/{id}`
