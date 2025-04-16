from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from models import Libro

app = FastAPI()

# Configurar la base de datos
register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

@app.get("/")
async def root():
    return {"mensaje": "API de Biblioteca funcionando 🚀"}
