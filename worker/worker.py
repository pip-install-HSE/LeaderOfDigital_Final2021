from celery import Celery
import torch
import torch.nn as nn
import torchvision
import shapely
import numpy as np

import requests
import geojson
	

# ToDo cfg
class Config:
    class MainServer:
        host = 'http://84.252.74.223:8080'
        # apiKey =

    class Celery:
        broker = 'redis://84.252.74.223:6379/0'


import pandas as pd

import sentinelhub
from sentinelhub import SHConfig, WebFeatureService, Geometry, CRS, DataCollection, SentinelHubRequest, MimeType, bbox_to_dimensions

from PIL import Image
import os, json
from secrets import token_hex
import warnings
warnings.filterwarnings('ignore')

class SentinelAPI(object):
    client_id = 'a9e3e184-d841-457d-96eb-64447e00b568'
    client_secret = '*7)_kA#Ov_4zf_%)Kh[2RdHu3ci7&dsuidbzt?z>'

    config = SHConfig()

    # config.instance_id = sentinelhub_instance_id

    config.sh_client_id = client_id
    config.sh_client_secret = client_secret

    @staticmethod
    def getDate(geom, datе, bands):
        betsiboka = Geometry(geometry=geom, crs=CRS.WGS84)

        evalscript = '''
        //VERSION=3
        function setup(){return{input:[{bands:''' + str(
            bands) + ''',units:"DN"}],output:{id:"default",sampleType:"FLOAT32",bands:''' + str(len(bands)) + '''}};}
        function evaluatePixel(sample) {return [ ''' + ','.join(map(lambda x: f'sample.{x}', bands)) + '''];}
        '''

        r = SentinelHubRequest(
            evalscript=evalscript,
            input_data=[SentinelHubRequest.input_data(data_collection=DataCollection.SENTINEL2_L1C, time_interval=datе,
                                                      mosaicking_order='leastCC')],
            responses=[SentinelHubRequest.output_response('default', MimeType.TIFF)],
            geometry=betsiboka,
            size=(64, 64),
            config=SentinelAPI.config,

        )

        r = r.get_data()[0]
        r = r.swapaxes(0, 2).swapaxes(1, 2)
        return dict(zip(bands, r))


app = Celery('Worker Classificatory', broker=Config.Celery.broker)


@app.task(name='simpleClassificatory')
def classificatory(data):
    polygon = data['geom']
    dateTime = data['dateTime']
    idObject = data['idObject']
    
    num_channels = 13
    
    model = torchvision.models.resnet101(pretrained=1)

    model.conv1 = nn.Conv2d(num_channels, model.conv1.out_channels,
                            kernel_size=model.conv1.kernel_size, stride=model.conv1.stride, padding=model.conv1.padding
                           )

    model.fc = nn.Sequential(
        nn.Linear(model.fc.in_features, 1)
    )
    state_dict = torch.load("BestModel.pt")
    model.load_state_dict(state_dict)
    
    # img = torch.randn(5, 13, 64, 64)
    
    geom = shapely.wkt.loads(polygon)
    bands = ["B01","B02","B03","B04","B05","B06","B07","B08","B8A","B09","B10","B11","B12","CLM","dataMask"]
    raw_data = SentinelAPI.getDate(geom, dateTime, bands)
    
    img = np.concatenate([raw_data[x].reshape(1, 64, 64) for x in bands[:13]], ).reshape((1, 13, 64, 64))
    img = torch.from_numpy(img) / 10000
    prediction = torch.sigmoid(model(img)).item()
    
    cloud_mask = raw_data["CLM"]
    
    cloud_percentage = np.count_nonzero(cloud_mask) / (64 * 64)
    
    # print(np.sum(cloud_mask))
    # print(cloud_mask[0:10, 0:10])
    
    r = requests.post(f'{Config.MainServer.host}/task/', json={
    	'geometry': geojson.Feature(geometry=geom, properties={}).geometry,
    	'data_datetime': dateTime,
    	'object_id': idObject,
    	'oil_spill_chance': prediction,
    	'cloudy': cloud_percentage,
    })
    
    
    return r.status_code, prediction

