#!/bin/bash

wget https://github.com/matterport/Mask_RCNN/releases/download/v2.0/mask_rcnn_coco.h5
wget http://images.cocodataset.org/zips/val2017.zip
unzip val2017.zip
mv val2017 images