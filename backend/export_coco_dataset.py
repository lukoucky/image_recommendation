from instance_segmentation_model import InstanceSegmentationModel
from dataset import Dataset

def generate_single(d):
	d.generate_features_by_one()

def generate_dataset(d):
	d.generate_dataset_pickles()
	print(len(d.get_image_names()))
	print(d.get_image_names()[0])

if __name__ == '__main__':
	model = InstanceSegmentationModel('mask_rcnn_coco.h5')
	d = Dataset('coco_segment', '/home/backend/val2017', model)
	# generate_single(d)
	generate_dataset(d)