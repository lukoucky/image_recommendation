from pixellib.instance import instance_segmentation
import pixellib


class InstanceSegmentationModel:
    # Name of categories of COCO dataset objects
    categories = ['BG', 'person', 'bicycle', 'car', 'motorcycle', 'airplane',
               'bus', 'train', 'truck', 'boat', 'traffic light',
               'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird',
               'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear',
               'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie',
               'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
               'kite', 'baseball bat', 'baseball glove', 'skateboard',
               'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
               'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
               'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
               'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed',
               'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
               'keyboard', 'cell phone', 'microwave', 'oven', 'toaster',
               'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors',
               'teddy bear', 'hair drier', 'toothbrush']
    
    def __init__(self, weights_path):
        self.weights_path = weights_path
        self.model = instance_segmentation()
        self.model.load_model(self.weights_path) 
    
    def predict_features(self, image_path):
        '''
        Runs instance segmentation on image located on image_path.
        :param image_path: file path of image
        :return: Feature vector with length same as categories. Each 
                 field in list represents probability that object for given
                 category is present on image.
        '''
        print(f'Segmenting {image_path}')
        segmask, output = self.model.segmentImage(image_path)
#         return self.prepare_feature_vector_count(segmask)
        return self.prepare_feature_vector_score(segmask)

    def predict(self, image_path):
        '''
        Runs instance segmentation on image located on image_path.
        :param image_path: file path of image
        :return: Dictionary with segmentaition categories and their image location
        '''
        print(f'Segmenting {image_path}')
        segmask, output = self.model.segmentImage(image_path)
        return segmask
        
    def print_categories(self, feature):
        '''
        Prints the human readable categoris represented on image based on predicted feature.
        Helper function fro debuging and tuning.
        :param feature: Feature computed in predict function
        '''
        print('Score  - Category')
        for category, score in enumerate(feature):
            if score > 0:
                print(f'{score:.4f} - {self.categories[category]}')
    
    def prepare_feature_vector_score(self, segmask):
        '''
        Generates feature vector from prediction output segmentation
        :param segmask: First output of segmentation
        :return: Feature vector with length same as categories. Each 
                 field in list represents probability that object for given
                 category is present on image.
        '''
        feature = [0]*len(self.categories)
        for i, category in enumerate(segmask['class_ids']):
            if feature[category] < segmask['scores'][i]:
                feature[category] = segmask['scores'][i]
        return feature
    
    def prepare_feature_vector_count(self, segmask):
        '''
        Generates feature vector from prediction output segmentation
        :param segmask: First output of segmentation
        :return: Feature vector with length same as categories. Each 
                 field in list represents number of occurences of object for given
                 category on image.
        '''
        feature = [0]*len(self.categories)
        for i, category in enumerate(segmask['class_ids']):
            feature[category] += 1
        return feature
