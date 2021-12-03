from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import json
import requests as req
from datetime import datetime
from datetime import timedelta
from sentinelhub.geo_utils import bbox_to_dimensions
import time
import shapely
import geojson
import shapely.geometry
import math
from celery import Celery

from shapely.geometry import shape, MultiPoint, LineString, MultiPolygon, Polygon, MultiLineString
from shapely.ops import transform
from shapely import geometry
from sentinelhub import BBoxSplitter, BBox, CRS, CustomUrlParam

from pyproj import Transformer, Proj


class Config:
    class MainServer:
        host = 'http://localhost:6379'
        # apiKey

    class Celery:
        broker = 'redis://localhost:6379/0'


app = Celery('Worker Classificatory', broker=Config.Celery.broker)


@app.task
def classify(data):
    polygon = data['geom']
    dateTime = data['dateTime']
    idObject = data['idObject']
    pass


class SatelliteObserver:
    sat_name = None
    bbox_history = []

    client_id = 'a9e3e184-d841-457d-96eb-64447e00b568'
    client_secret = '*7)_kA#Ov_4zf_%)Kh[2RdHu3ci7&dsuidbzt?z>'

    bbox = [-90.0, -180.0, 90.0, 180.0]
    last_date = None
    datetime_interval = None

    limit = 50
    cloud_cover = 100

    def __init__(self, sat_name: str):
        # bb = [-18.2214723362962, -72.1649134541609, -14.877867861463805, -69.11191008520701]
        # for i in range(4):
        #      bb[i] /= 2
        #      r = req.post("http://84.252.74.223:8080/objects",
        #      json={"id": 2179789,
        #            'geometry':  geojson.Feature(geometry=self.bbox_to_polygon(bb), properties={}).geometry,
        #            "name": "Test7",
        #            "padding": 1.2})

        #print(r.text)

        self.sat_name = sat_name

    def get_json(self):
        client = BackendApplicationClient(client_id=self.client_id)
        oauth = OAuth2Session(client=client)
        token = oauth.fetch_token(token_url='https://services.sentinel-hub.com/oauth/token',
                                  client_secret=self.client_secret)

        url = "https://services.sentinel-hub.com/api/v1/catalog/search"
        headers = {'Authorization': 'Bearer ' + token['access_token'], "content-type": "application/json"}
        payload = {'bbox': self.bbox,
                   'collections': [self.sat_name],
                   'datetime': self.datetime_interval,
                   'limit': self.limit,
                   "query": {"eo:cloud_cover": {"lte": self.cloud_cover}}}

        r = req.post(url, headers=headers, data=json.dumps(payload))

        return r.text

    def get_bboxs(self):
        raw_json = json.loads(s.get_json())
        return [f['bbox'] for f in raw_json['features']], [f['properties']['datetime'] for f in raw_json['features']]

    def get_string_datetime_interval(self, d1, d2):
        string_now = d2.strftime("%Y-%m-%dT%H:%M:%SZ")
        string_past = d1.strftime("%Y-%m-%dT%H:%M:%SZ")
        return string_past + "/" + string_now

    def get_from_api(self, wkt): #todo
        print(wkt)
        r = req.post("http://84.252.74.223:8080/inspect_objects", params = {'big_geometry': wkt})
        print(r.text)
        return r.text

    def bbox_to_polygon(self, bbox):
        polygon = shapely.geometry.box(*bbox, ccw=True)
        return polygon

    def from_obj_to_buffer(self, obj, buffer_value):

        _lon, _lat = obj.centroid.coords[0]
        aeqd = Proj(proj='aeqd', ellps='WGS84', datum='WGS84',
                    lat_0=_lat, lon_0=_lon)
        wgs84_globe = Proj(proj='latlong', ellps='WGS84')

        transformer = Transformer.from_proj(wgs84_globe, aeqd)
        deTransformer = Transformer.from_proj(aeqd, wgs84_globe)

        obj = transform(transformer.transform, obj)
        obj = obj.buffer(buffer_value)
        obj = transform(deTransformer.transform, obj)
        return obj



    def process_bbox(self, bbox, time):
        poly = self.bbox_to_polygon(bbox)
        wkt = poly.wkt

        objects = self.get_from_api(wkt)
        pass
        for obj in objects:
            obj = self.from_obj_to_buffer(obj['poly'], obj['buffer'])
            # obj_geom = Geometry(geometry=p, crs=CRS.WGS84)
            obj_size = bbox_to_dimensions(obj.bounds, resolution=1)

            r = list(map(lambda x: math.ceil(x / 64), obj_size))

            bbox_splitter = BBoxSplitter([obj], CRS.WGS84, r)
            splitted = bbox_splitter.get_bbox_list()

            for s in splitted:
                data = {'geom': self.bbox_to_polygon(s).wkt,
                        'dateTime': time,
                        'obj': obj.id}

                app.send_task('classify', args={data, })



    def run_user_request(self, bbox, time):
        self.process_bbox(bbox, time)


    def run(self):
        data = [[], []]
        time_skip = -60
        while not data[0]:
            time_skip += 60
            print("wait:", time_skip)
            self.datetime_interval = self.get_string_datetime_interval(datetime.now() - timedelta(minutes=time_skip),
                                                                       datetime.now())
            data = self.get_bboxs()
        str_last_date = data[1][0]
        self.last_date = datetime.strptime(str_last_date, "%Y-%m-%dT%H:%M:%SZ")
        total = 0
        while True:
            self.datetime_interval = self.get_string_datetime_interval(self.last_date + timedelta(seconds=0),
                                                                       datetime.now())
            bboxs, times = self.get_bboxs()
            if bboxs:
                str_last_date = times[0]
                self.last_date = datetime.strptime(str_last_date, "%Y-%m-%dT%H:%M:%SZ")
            total += len(bboxs)
            print(self.datetime_interval)
            print(bboxs, times)
            print(len(bboxs))
            print(total)

            for i in range(len(bboxs) - 1, -1, -1):  # todo fix rerun
                self.process_bbox(bboxs[i], times[i])

            time.sleep(10)


if __name__ == "__main__":
    # app = Celery('Worker Classificatory', broker=Config.Celery.broker)
    s = SatelliteObserver("sentinel-2-l2a")
    s.run()


