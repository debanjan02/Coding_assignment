"""
Create HTML layout from given coordinates. Take input for JSON file for the time being.
Inputs are,
    1/ Height, Width of input image.
    2/ (Top, Left), (Bottom, Right) coordinates for each UI element in image.
NOTE: coordinates are calculated w.r.t dimensions of image.

Execute as (without quotes):
    `python layout.py -a <assets_folder> -i <json_file>`

"""

import os
import argparse

import cv2
import numpy as np

import json
from pprint import pprint

""" Argument parser """
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input',  type=str, required=True, help='JSON file as input.')
parser.add_argument('-a', '--assets', type=str, required=True, help='Assets folder.')

""" Parse arguments """
args = parser.parse_args()
input_fn = args.input
assets_dir = args.assets

"""
Overlay an PNG image on another
"""
def overlay_transparent(background, overlay, x, y):
    background_width = background.shape[1]
    background_height = background.shape[0]

    if x >= background_width or y >= background_height:
        return background

    h, w = overlay.shape[0], overlay.shape[1]

    if x + w > background_width:
        w = background_width - x
        overlay = overlay[:, :w]

    if y + h > background_height:
        h = background_height - y
        overlay = overlay[:h]

    if overlay.shape[2] < 4:
        overlay = np.concatenate(
            [
                overlay,
                np.ones((overlay.shape[0], overlay.shape[1], 1), dtype = overlay.dtype) * 255
            ],
            axis = 2,
        )

    overlay_image = overlay[..., :3]
    mask = overlay[..., 3:] / 255.0

    background[y:y+h, x:x+w] = (1.0 - mask) * background[y:y+h, x:x+w] + mask * overlay_image

    return background

""" Read JSON input """
with open(input_fn) as input:
    data = json.load(input)
# pprint(data)

"""
Create a simple visualization using given assets.

NOTE:
    Just create a white image the same size as the input image and place given assets for HTML components on it in given
    coordinates.
    The assets have a minimum size. It is suggested to retain the minimum width, height of asset (looks better). But if
    necessary assets can be resized.
"""

height = int(data['height'])
width = int(data['width'])

background = np.zeros((height, width, 3), np.uint8)
background[:] = (255, 255, 255)

#creating margin
for item in data['results']:
    if(item['left'] < 200):
        item['left']=200

#align horizontally       
for item1 in data['results']:
    for item2 in data['results']:
        if(abs(item1['left']-item2['left'])<200 and item1['top']-item2['top']> 20):
           item2['left']=item1['left']
#align vertically
for item1 in data['results']:
    for item2 in data['results']:
        if(abs(item1['top']-item2['top'])<200 and item1['left']-item2['left']>20):
            item2['top']=item1['top']
            
#centre alignment of footer            
for item in data['results']:
    class_name = item['class']
    if(class_name == 'Footer'):
        #print(item['left'])
        #print(item['right'])
        #print(data['width'])
        #item_w = item['right']-item['left']
        #middle = int(int(data['width'])/2)
        item['left']=420
        #item['left']=middle-int(item_w/2)
        #print(item['left'])
        #print(type(item['left']))


for item in data['results']:
    class_name = item['class']

    asset_fn = os.path.join(assets_dir, class_name + '.png')
    overlay = cv2.imread(asset_fn)

    left = item['left']
    top = item['top']

    background = overlay_transparent(background, overlay, left, top)

fn_output = os.path.splitext(input_fn)[0] + '_out.jpg'
cv2.imwrite(fn_output, background)
