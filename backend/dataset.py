from sklearn.neighbors import NearestNeighbors
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import random
import pickle
import os


class Dataset:
    '''
    Helper class for image dataset. Used mainly during initial implementation and debugging. 
    Holds information about dataset, export features to and from pickles
    and plots images. 
    '''
    # List of allowed image file extensions
    ALLOWED_IMG_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif', 'tiff']

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

    def __init__(self, name, images_path, model=None):
        self.name = name
        self.images_path = images_path
        self.features_pickle_filename = f'features_{name}.pickle'
        self.imagenames_pickle_filename = f'imagenames_{name}.pickle'
        self.model = model
        self.feature_dict = None
        self.features = None
        self.image_names = None
        
    def load_features(self):
        '''
        Loads precomputed features from pickle. If the piclke does not exist it will
        generate features by calling generate_and_save_features() method
        :return: Dictionary where key is image file name and value it's veature vector
        '''
        if not self.feature_dict is None:
            return self.feature_dict
            
        if not os.path.isfile(self.features_pickle_filename):
            self.generate_and_save_features()
            
        if not os.path.isfile(self.imagenames_pickle_filename):
            self.generate_and_save_features()
        
        feature_dict = {}
        feature_list = pickle.load(open(self.features_pickle_filename, 'rb'))
        names = pickle.load(open(self.imagenames_pickle_filename, 'rb'))
        self.features = feature_list
        self.image_names = names

        feature_dict = {}
        for i, name in enumerate(names):
            feature_dict[name] = feature_list[i]
            
        self.feature_dict = feature_dict
        return feature_dict
    
    def get_features(self):
        '''
        Return list with features for all images in dataset. Order in the list
        is the same as in image names list.
        :return: List of features for all images in dataset
        '''
        if self.features is None:
            self.load_features()
        return self.features
    
    def get_features_for_image(self, image_name):
        '''
        :param image_name: File name of image from dataset
        :return: Features for image with name given in image_name parameter
        '''
        if self.feature_dict is None:
            self.load_features()
        if not image_name in self.feature_dict:
            print(f'Image {image_name} is not in Database')
            return [0]*81
        return self.feature_dict[image_name]
    
    def get_image_names(self):
        '''
        Return list with names of all images in dataset. Order in the list
        is the same as in feature list.
        :return: List with names of all images in dataset
        '''
        if self.image_names is None:
            self.load_features()
        return self.image_names
        
    def generate_and_save_features(self):
        '''
        Computes featers for all images in dataset and store them in pickle.
        It expects that model is set and that folder with images exists.
        '''
        if not self.can_generate_features():
            return
        
        print(f'Generating features from images in {self.images_path}')
        imgs = self.get_images_from_dir()
        feature_list = []
        for image in imgs:
            features = self.model.predict(os.path.join(self.images_path, image))
            feature_list.append(features)
        pickle.dump(feature_list, open(self.features_pickle_filename, 'wb'))
        pickle.dump(imgs, open(self.imagenames_pickle_filename, 'wb'))

    def generate_features_by_one(self):
        '''
        Computes featers for all images in dataset and store them in pickle - one pickle per image.
        It expects that model is set and that folder with images exists.
        '''
        if not self.can_generate_features():
            return

        folder_name = f'{self.name}_pickles'

        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)
        
        print(f'Generating features from images in {self.images_path}')
        imgs = self.get_images_from_dir()
        for image in imgs:
            pickle_name = f'{folder_name}/{os.path.splitext(image)[0]}.pickle'
            if os.path.isfile(pickle_name):
                print(f'pickle {pickle_name} already exist - skipping')
                continue
            print(f'Predictiong image {image}')
            features = self.model.predict(os.path.join(self.images_path, image))
            pickle.dump(features, open(pickle_name, 'wb'))

    def generate_dataset_pickles(self):
        '''
        Takes pickles per image generated by method generate_features_by_one() and 
        creates pickle for the whole database. 
        '''
        folder_name = f'{self.name}_pickles'
        if not os.path.isdir(folder_name):
            print(f'Folder for pickles does not exist')
            return

        feature_list = []
        image_names = []
        for pickle_path in os.listdir(folder_name):
            if pickle_path.endswith('.pickle'):
                print(f'Working on pickle {pickle_path}')
                img_name = f'{os.path.splitext(pickle_path)[0]}.jpg'
                image_names.append(img_name)
                features = pickle.load(open(os.path.join(folder_name, pickle_path), 'rb'))
                feature_list.append(self.model.prepare_feature_vector_score(features))

        pickle.dump(feature_list, open(self.features_pickle_filename, 'wb'))
        pickle.dump(image_names, open(self.imagenames_pickle_filename, 'wb'))
        self.load_features()


    def can_generate_features(self):
        '''
        Checks if features from images can be generated (folder with images exist and model is set)
        :return: True if features from images can be generated
        '''
        if not os.path.isdir(self.images_path):
            print(f'Folder {self.images_path} does not exist. Cannot generate features.')
            return False
    
        if self.model is None:
            print(f'Dataset {self.name} does not have any model set. Cannot generate features.')
            print(f'Use set_model() method to set model with predict function.')
            return False
        return True
        
    def get_images_from_dir(self):
        '''
        :return: List with all images in directory set in constructor.
        '''
        imgs = []
        for img_path in os.listdir(self.images_path):
            if self.is_image(img_path):
                imgs.append(img_path)
        return imgs
    
    def get_random_image(self):
        '''
        :return: File name of one random image from dataset
        '''
        images = self.get_image_names()
        return random.choice(images)
    
    def plot_images(self, image_dict, original):
        '''
        Plots all images from image_dict plus original image.
        Helper function fro debuging and tuning.
        :param image_dict: Dictionary where keys are the names of images and value are similarity
                           score to original image
        :param original: Image name of searched image
        '''
        images = list(image_dict.keys())
        scores = list(image_dict.values())

        n_imgs = len(images) + 1
        rows = n_imgs//2
        columns = 2
        if n_imgs == 1:
            rows = 1
            columns = 1

        fig = plt.figure(figsize=(19,4*rows))
        images = [original]+images
        for i, image_path in enumerate(images):
            img = mpimg.imread(os.path.join(self.images_path, image_path))
            ax = fig.add_subplot(rows+1, columns, i+1)
            if i == 0:
                ax.title.set_text(f'Original Image ({image_path})')
            else:
                ax.title.set_text(f'{image_path} - score: {scores[i-1]:.4f}')
            ax.imshow(img)
            ax.axis('off')
        plt.show()

    def get_objects_on_image(self, image_name):
        '''
        :param image_name: Name of image for object search
        :return: Dictionary where key is name of object on image and value it probablity 
        '''
        objects = dict()
        feature = self.get_features_for_image(image_name)
        for category, score in enumerate(feature):
            if score > 0:
                objects[self.categories[category]] = score
        return objects

    def get_similar_images(self, image_name, n=10):
        '''
        For given image_name returns most simailar images in dataset.
        :param image_name: Image name of searched image
        :return: Dictionary where keys are the names of images and value are similarity
                 score to original image
        '''
        similar: dict = {}
        feature_dict = self.load_features()

        my_features = self.get_features_for_image(image_name)
        feature_list = list(feature_dict.values())

        neighbors = NearestNeighbors(n_neighbors=n, algorithm='brute', metric='euclidean').fit(feature_list)
        distances, indices = neighbors.kneighbors([my_features])
        names = self.get_image_names()
        
        for i in range(len(distances[0])):
            similar[names[indices[0][i]]] = distances[0][i]

        return similar
    
    def is_image(self, filename):
        '''
        Check if file located in filename is an image.
        It checks only by the extension.
        :param filename: Tested file name
        :return: True if file is image, False otherwise
        '''
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_IMG_EXTENSIONS
            