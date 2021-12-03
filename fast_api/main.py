from typing import List
import logging
from fastapi import FastAPI, HTTPException
from models import Objects, Object_Pydantic, Task_Pydantic, Tasks, Tags, Tag_Pydantic
from pydantic import BaseModel
from decouple import config
from starlette.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import HTTPNotFoundError, register_tortoise
from shapely.geometry import shape

logger = logging.getLogger(__name__)
app = FastAPI(title="Tortoise ORM FastAPI example", debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Status(BaseModel):
    message: str


@app.get("/objects", response_model=List[Object_Pydantic])
async def get_objects():
    return await Object_Pydantic.from_queryset(Objects.all())


@app.post("/objects", response_model=Object_Pydantic)
async def create_user(user: Object_Pydantic):
    print(user.dict(exclude_unset=True))
    user_obj = await Objects.create(**user.dict(exclude_unset=True))
    return await Object_Pydantic.from_tortoise_orm(user_obj)


@app.post("/inspect_objects")
async def inspect_objects(big_geometry):
    # big_geometry = shape(big_geometry)
    query = f"SELECT id, geometry, name, padding FROM objects WHERE ST_Intersects(ST_GeomFromGeoJSON(geometry), '{big_geometry}'::geography::geometry)"
    # print(query)
    objects = await Objects.raw(query)
    print(objects, [o.id for o in objects])
    # print(objects)
    return await Object_Pydantic.from_queryset(Objects.filter(id__in=[o.id for o in objects]))


@app.get(
    "/object/", response_model=Object_Pydantic, responses={404: {"model": HTTPNotFoundError}}
)
async def get_user(user_id: int):
    return await Object_Pydantic.from_queryset_single(Objects.get(id=user_id))


@app.put(
    "/object/", response_model=Object_Pydantic, responses={404: {"model": HTTPNotFoundError}}
)
async def update_user(object_id: int, user: Object_Pydantic):
    await Objects.filter(id=object_id).update(**user.dict(exclude_unset=True))
    return await Object_Pydantic.from_queryset_single(Objects.get(id=user_id))


@app.delete("/object/", response_model=Status, responses={404: {"model": HTTPNotFoundError}})
async def delete_user(object_id: int):
    deleted_count = await Objects.filter(id=object_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"Object {object_id} not found")
    return Status(message=f"Deleted object {object_id}")

# print(f"postgres://{config('POSTGRES_USER')}:{config('POSTGRES_PASSWORD')}@{config('POSTGRES_HOST')}:{config('POSTGRES_PORT')}/{config('POSTGRES_DB')}")


TORTOISE_ORM = {
    "connections": {"default": f"postgres://{config('POSTGRES_USER')}:{config('POSTGRES_PASSWORD')}@{config('POSTGRES_HOST')}:{config('POSTGRES_PORT')}/{config('POSTGRES_DB')}"},
    "apps": {
        "models": {
            "models": ["models"],
            "default_connection": "default",
        },
    },
}


register_tortoise(
    app,
    # db_url=f"postgres://{config('POSTGRES_USER')}:{config('POSTGRES_PASSWORD')}@{config('POSTGRES_HOST')}:{config('POSTGRES_PORT')}/{config('POSTGRES_DB')}",
    config=TORTOISE_ORM,
    # modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

