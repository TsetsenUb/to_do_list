from fastapi import FastAPI, status

from app.modules.tasks import tasks_router
from app.modules.users import users_router


app = FastAPI(title="Мой todo list")

app.include_router(tasks_router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(users_router, prefix="/api/users", tags=["Users"])


@app.get("/", status_code=status.HTTP_200_OK)
async def get_hello():
    return {"message": "Hello!"}
