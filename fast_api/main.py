# from tortoise import Tortoise
# Tortoise.init_models(["model1", ".model2", "fast_api.model3"], "models")
import json
from datetime import datetime
from typing import List
import logging
from fastapi import FastAPI, HTTPException

from model1 import Task_Pydantic
from model2 import Tag_Pydantic
from model3 import Object_Pydantic
from models import Objects, Tasks
from pydantic import BaseModel
from decouple import config
from starlette.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import HTTPNotFoundError, register_tortoise

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


@app.post("/inspect_objects")
async def inspect_objects(big_geometry):
    # big_geometry = shape(big_geometry)
    query = f"SELECT id, geometry, name, padding FROM objects WHERE ST_Intersects(ST_GeomFromGeoJSON(geometry), '{big_geometry}'::geography::geometry)"
    # print(query)
    objects = await Objects.raw(query)
    print(objects, [o.id for o in objects])
    # print(objects)
    return await Object_Pydantic.from_queryset(Objects.filter(id__in=[o.id for o in objects]))


# апишка поиска по объекта
#

@app.get("/tasks/", response_model=List[Task_Pydantic])
async def get_objects():
    res = await Tasks.all().values()
    # raise Exception(list(res))
    return await Task_Pydantic.from_queryset(Tasks.all())


@app.post("/task/", response_model=Task_Pydantic)
async def create_task(task: Task_Pydantic):
    task_dict = task.dict(exclude_unset=True)
    task_dict['object'] = await Objects.get(id=21474847)
    # x = Objects.get(id=task_dict['object'])
    # task_dict['object'] = Tasks.get(id=task_dict['object'])
    # if 1 == 1:
    # raise Exception(x)
    task_obj = await Tasks.create(**task_dict)
    return await Task_Pydantic.from_tortoise_orm(task_obj)


@app.get("/task/", response_model=Task_Pydantic,
         responses={404: {"model": HTTPNotFoundError}})
async def get_task(task_id: int):
    return await Task_Pydantic.from_queryset_single(Tasks.get(id=task_id))


@app.put("/task/", response_model=Task_Pydantic,
         responses={404: {"model": HTTPNotFoundError}})
async def update_task(task_id: int, user: Task_Pydantic):
    await Tasks.filter(id=task_id).update(**user.dict(exclude_unset=True))
    return await Task_Pydantic.from_queryset_single(Tasks.get(id=task_id))


@app.delete("/task/", response_model=Status, responses={404: {"model": HTTPNotFoundError}})
async def delete_task(task_id: int):
    deleted_count = await Tasks.filter(id=task_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"Object {task_id} not found")
    return Status(message=f"Deleted object {task_id}")


@app.get("/objects", response_model=List[Object_Pydantic])
async def get_objects():
    return await Object_Pydantic.from_queryset(Objects.all())


@app.get("/object/",
         response_model=Object_Pydantic,
         responses={404: {"model": HTTPNotFoundError}})
async def get_object(user_id: int):
    return await Object_Pydantic.from_queryset_single(Objects.get(id=user_id))


@app.post("/object", response_model=Object_Pydantic)
async def create_object(user: Object_Pydantic):
    user_dict = user.dict(exclude_unset=True)
    # user_dict['object'] = Tasks.get(id=user_dict['object'])
    # raise Exception(str(user_dict))
    user_obj = await Objects.create(**user_dict)
    return await Object_Pydantic.from_tortoise_orm(user_obj)


@app.put("/object/",
         response_model=Object_Pydantic,
         responses={404: {"model": HTTPNotFoundError}})
async def update_object(object_id: int, user: Object_Pydantic):
    await Objects.filter(id=object_id).update(**user.dict(exclude_unset=True))
    return await Object_Pydantic.from_queryset_single(Objects.get(id=object_id))


@app.delete("/object/", response_model=Status, responses={404: {"model": HTTPNotFoundError}})
async def delete_object(object_id: int):
    deleted_count = await Objects.filter(id=object_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"Object {object_id} not found")
    return Status(message=f"Deleted object {object_id}")


# print(f"postgres://{config('POSTGRES_USER')}:{config('POSTGRES_PASSWORD')}@{config('POSTGRES_HOST')}:{config('POSTGRES_PORT')}/{config('POSTGRES_DB')}")

@app.get("/search/")
def read_item(object_name: str):
    # objects = ['Завод имени Чкалова', 'Завод имени Петрова', 'Трубопровод Петечкина']
    with open('admin_level_3.geojson', 'r') as file:
        geojson = json.loads(file.read())
    features = geojson['features']
    objects = [(feature['properties']['name'], i) for i, feature in enumerate(features)]
    result = []
    filtered_geojson = geojson
    filtered_geojson['features'] = []
    for name, i in objects:
        if name.lower() in object_name.lower() or object_name.lower() in name.lower():
            filtered_geojson['features'].append(features[i])
            result.append({
                "id": i,
                # "geometry": features[i]['geometry'],
                "name": name,
                "tags": {"Организация": "ООО Газпром"},
                "padding": 10
            })

    print(len(result))
    return result, filtered_geojson


@app.post("/oil_spills/")
def oil_spills(object_ids: List[str], ):
    return [object_ids]


TORTOISE_ORM = {
    "connections": {
        "default": f"postgres://{config('POSTGRES_USER')}:{config('POSTGRES_PASSWORD')}@{config('POSTGRES_HOST')}:{config('POSTGRES_PORT')}/{config('POSTGRES_DB')}"},
    "apps": {

    },
}



register_tortoise(
    app,
    db_url=f"postgres://{config('POSTGRES_USER')}:{config('POSTGRES_PASSWORD')}@{config('POSTGRES_HOST')}:{config('POSTGRES_PORT')}/{config('POSTGRES_DB')}",
    # config=TORTOISE_ORM,
    modules={"models": ["model1", "model2", "model3"]},
# "models": {
#             "models": ["model1", "model2", "model3"],
#             "default_connection": "default",
#         },
    generate_schemas=True,
    add_exception_handlers=True,
)


