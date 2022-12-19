import uvicorn

from api.api import create_app
from api.database import create_tables, connection

app = create_app()


@app.on_event("startup")
async def startup_event():
    create_tables()


@app.on_event("shutdown")
def shutdown_event():
    connection.close()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=43122)
