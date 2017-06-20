# -*- coding: utf-8 -*-
"""
Created on Tue Jun  20 10:00:10 2017

@author: Thomas Schatz

Example code for fetching data from our OSF repository.
This just prints a list of the elements in the /Stimuli/
folder of our osfstorage component.
"""

import jsonapi_requests
import os.path as p
from _osf_auth import osf_username, osf_password


api = jsonapi_requests.Api.config({ 'API_ROOT': 'https://api.osf.io/v2/',
                                    'AUTH':(osf_username, osf_password),
                                    'TIMEOUT': 20})
storage_root = "https://api.osf.io/v2/nodes/zdtk7/files/osfstorage"
endpoint = api.endpoint(storage_root)
response = endpoint.get()
for  item in response.data:
  if item.attributes['materialized_path'] == '/Stimuli/':
    path = item.attributes['path']
    break
stimuli_url = p.join(storage_root, path[1:])
endpoint = api.endpoint(stimuli_url)
response = endpoint.get()
for item in response.data:
  print(item.attributes['materialized_path'])