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
from sentinelhub import Geometry
from shapely.geometry import shape, MultiPoint, LineString, MultiPolygon, Polygon, MultiLineString
from shapely.ops import transform
from shapely import geometry
from sentinelhub import BBoxSplitter, BBox, CRS, CustomUrlParam

from pyproj import Transformer, Proj


class Config:
    class MainServer:
        host = 'http://84.252.74.223:8080'
        # apiKey

    class Celery:
        broker = 'redis://84.252.74.223:6379/0'


app = Celery('Worker Classificatory')
app.conf.broker_url = 'redis://84.252.74.223:6379/0'


@app.task(name='simpleClassificatory')
def classificatory(data):
    geom = data['geom']
    dateTime = data['dateTime']
    idObject = data['idObject']


class SatelliteObserver:
    sat_name = None
    bbox_history = []

    client_id = 'a9e3e184-d841-457d-96eb-64447e00b568'
    client_secret = '*7)_kA#Ov_4zf_%)Kh[2RdHu3ci7&dsuidbzt?z>'

    bbox = [73.81, 60.41, 78.81, 62.41]
    last_date = None
    datetime_interval = None

    limit = 50
    cloud_cover = 100

    def __init__(self, sat_name):
        # bb = [-89.7614191199703, 57.64588130076059, -89.47974163634458, 57.75086192489303]
        # r = req.post("http://84.252.74.223:8080/object",
        # json={"id": 2731192,
        #         'geometry':  geojson.Feature(geometry=self.bbox_to_polygon(bb), properties={}).geometry,
        #         "name": "Test0001",
        #         "padding": 1})
        #
        # print(r.text)

        self.sat_name = sat_name

    def get_json(self):
        client = BackendApplicationClient(client_id=self.client_id)
        oauth = OAuth2Session(client=client)
        token = oauth.fetch_token(token_url='https://services.sentinel-hub.com/oauth/token',
                                  client_secret=self.client_secret)

        url = 'https://services.sentinel-hub.com/api/v1/catalog/search'
        headers = {'Authorization': 'Bearer ' + token['access_token'], 'content-type': 'application/json'}
        payload = {'bbox': self.bbox,
                   'collections': [self.sat_name],
                   'datetime': self.datetime_interval,
                   'limit': self.limit,
                   'query': {'eo:cloud_cover': {'lte': self.cloud_cover}}}

        r = req.post(url, headers=headers, data=json.dumps(payload))
        return r.json()

    def get_bboxs(self):
        raw_json = self.get_json()
        return [f['bbox'] for f in raw_json['features']], [f['properties']['datetime'] for f in raw_json['features']]

    def get_string_datetime_interval(self, d1, d2):
        string_now = d2.strftime("%Y-%m-%dT%H:%M:%SZ")
        string_past = d1.strftime("%Y-%m-%dT%H:%M:%SZ")
        return string_past + "/" + string_now

    def get_from_api(self, wkt):  # todo
        r = req.post("http://84.252.74.223:8080/inspect_objects", params={'big_geometry': wkt})
        print(r.text)
        if not r:
            return r
        return r.json()

    def bbox_to_polygon(self, bbox):
        polygon = shapely.geometry.box(*bbox, ccw=True)
        return polygon

    def from_obj_to_buffer(self, obj, buffer_value, sat_poly):  # todo make buffer
        if obj['type'] == 'LineString':
            obj = LineString(obj["coordinates"])
        else:  # obj['type'] == "Polygon":
            obj = Polygon(obj["coordinates"][0])
            obj = obj.intersection(sat_poly)

        if obj.is_empty:
            return obj
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

    def process_bbox_sat(self, bbox, time, p=0):
        poly = self.bbox_to_polygon(bbox)
        wkt = poly.wkt

        objects = self.get_from_api(wkt)
        for obj in objects:
            id = obj['id']
            obj = self.from_obj_to_buffer(obj['geometry'], obj['padding'], poly)
            print(obj)
            obj_geom = Geometry(geometry=obj, crs=CRS.WGS84)
            obj_size = bbox_to_dimensions(obj_geom.bbox, resolution=1)

            r = list(map(lambda x: math.ceil(x / 64), obj_size))
            print(r)
            bbox_splitter = BBoxSplitter([obj], CRS.WGS84, r)
            splitted = bbox_splitter.get_bbox_list()
            print(len(splitted))

            for s in splitted:
                data = {'geom': self.bbox_to_polygon(s).wkt,
                        'dateTime': time,
                        'idObject': id}
                print("created")
                print(data)
                print(app.control.inspect())
                app.send_task('simpleClassificatory', args=[data, ], priority=p)
                print(app.control.inspect())
                print("OK")

    def run_user_request(self, bbox, time):
        self.process_bbox_sat(bbox, time)

    def process_bbox_obj(self, objects, bbox_sat, time_sat, p=0):
        poly = self.bbox_to_polygon(bbox_sat)
        wkt = poly.wkt

        # objects = [self.get_from_api(wkt)]
        for obj in objects:
            id = obj['id']
            obj = self.from_obj_to_buffer(obj['geometry'], obj['padding'], poly)
            if obj.is_empty:
                print(obj)
                continue
            print("OK")

            obj_geom = Geometry(geometry=obj, crs=CRS.WGS84)
            obj_size = bbox_to_dimensions(obj_geom.bbox, resolution=1)

            r = list(map(lambda x: math.ceil(x / 64), obj_size))
            print(r)
            bbox_splitter = BBoxSplitter([obj], CRS.WGS84, r)
            splitted = bbox_splitter.get_bbox_list()
            print(len(splitted))

            for s in splitted:
                data = {"geom": self.bbox_to_polygon(s).wkt,
                        "dateTime": time_sat,
                        "idObject": id}
                print("created")
                print(data)
                app.send_task('simpleClassificatory', args=[data, ])
                print("OK")

    '''for single run for single task from real user'''

    def worker_run(self, object_bbox, datetime_interval):
        self.datetime_interval = datetime_interval
        bboxs, times = self.get_bboxs()
        if not bboxs:
            return False
        for i in range(len(bboxs) - 1, -1, -1):  # todo fix rerun
            self.process_bbox_obj(bboxs[i], times[i], 3)
        return True

    def worker_all_obj(self, interval="2021-09-07T00:00:00Z/2021-09-14T00:00:00Z"):
        r = geojson.loads(req.get("http://84.252.74.223:8080/objects").text)
        print(req.get("http://84.252.74.223:8080/objects").text)
        print(r)
        self.datetime_interval = interval
        self.limit = 100
        sat_bboxs, sat_times = self.get_bboxs()
        print(len(sat_bboxs))
        for i in range(len(sat_bboxs)):
            self.process_bbox_obj(r, sat_bboxs[i], sat_times[i], p=3)

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
            print(len(bboxs), total)

            for i in range(len(bboxs) - 1, -1, -1):  # todo fix rerun
                self.process_bbox_sat(bboxs[i], times[i])

            time.sleep(1)


if __name__ == "__main__":
    # app = Celery('Worker Classificatory', broker=Config.Celery.broker)
    s = SatelliteObserver(r"sentinel-2-l2a")

    str_last_date = "2020-02-14T00:02:00Z"
    last_date = datetime.strptime(str_last_date, "%Y-%m-%dT%H:%M:%SZ")
    for i in range(100):
        string_time = s.get_string_datetime_interval(last_date, last_date + timedelta(minutes=60))
        s.worker_all_obj(string_time)
        last_date = last_date + timedelta(minutes=60)
    # s.worker_all_obj('2021-03-14T23:00:00Z/2021-03-15T18:00:00Z')
    # s.run()

    # test = {'bbox': [-90.0, -180.0, 90.0, 180.0]}
    # res = json.dumps(test)
    # print(res)
