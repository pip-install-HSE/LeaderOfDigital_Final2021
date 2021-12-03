from fastapi import FastAPI
import json
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    file = open('us-states.geojson.txt', 'r')
    geojson = json.loads(file.read())
    file.close()

    return geojson


@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}


def huy(name, geometry):
    return {
        "id": 1,
        "geometry": geometry,
        "name": name,
        "tags": {"Организация": "ООО Газпром"},
        "padding": 10
    }


@app.get("/search/")
def read_item(object_name: str):
    object_name = object_name.lower()
    # objects = ['Завод имени Чкалова', 'Завод имени Петрова', 'Трубопровод Петечкина']
    with open('us-states.geojson.txt', 'r') as file:
        geojson = json.loads(file.read())
    features = geojson['features']
    objects = [(feature['properties']['name'], i) for i, feature in enumerate(features)]
    objects = [(name.lower(), i) for (name, i) in objects]
    result = []
    for name, i in objects:
        if name in object_name or object_name in name:
            result.append({
                "id": 1,
                "geometry": features[i]['geometry'],
                "name": name,
                "tags": {"Организация": "ООО Газпром"},
                "padding": 10
            })
    print(len(result))
    return result
