from instance_segmentation_model import InstanceSegmentationModel
from dataset import Dataset

model = InstanceSegmentationModel('mask_rcnn_coco.h5')
d = Dataset('coco_segment', '/home/backend/val2017_b', model);
d.get_image_names()
