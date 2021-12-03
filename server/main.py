from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json

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


@app.get("/search/")
def read_item(object_name: str):
    # objects = ['Завод имени Чкалова', 'Завод имени Петрова', 'Трубопровод Петечкина']
    with open('us-states.geojson.txt', 'r') as file:
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


@app.get("/get_object/")
def read_item(object_id: int):
    with open('us-states.geojson.txt', 'r') as file:
        geojson = json.loads(file.read())
    geojson['features'] = [geojson['features'][object_id]]
    print(geojson)
    return geojson


@app.get("/objects_near/")
def read_item(polygon: str):
    # делаем запрос к бд, возвращаем рядом которые с учетом паддингов
    return None
