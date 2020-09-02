from keras.applications.resnet50 import ResNet50
from keras.applications.resnet50 import preprocess_input, decode_predictions

from keras.applications.nasnet import NASNetLarge
from keras.applications.nasnet import preprocess_input, decode_predictions

from keras.preprocessing import image
from keras.models import Model
import numpy as np

from os.path import join
from utils import is_image, get_all_images_in_dir

resnet50_model = ResNet50(weights='imagenet')

def predict(img_path : str, model: Model):
    print('Predicting',img_path)
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    features = model.predict(x)
    flattened_features = features.flatten()
    normalized_features = flattened_features / np.linalg.norm(flattened_features)
    return normalized_features

def predict_resnet50(img_path: str):
    return predict(img_path, resnet50_model)

def findDifference(f1, f2):
    return np.linalg.norm(f1-np.array(f2))

def findDifferences(feature_vectors, image_name):
    similar: dict = {}
    for k, v in feature_vectors.items():
        if not (k == image_name):
            diff=findDifference(feature_vectors[k],feature_vectors[image_name])
            similar[k] = diff
    return similar 

def similarity_resnet50(image_name):
    model = ResNet50(weights='imagenet')
    return compute_similarity(image_name, model)

def similarity_nasnet_large(image_name):
    model = NASNetLarge(weights='imagenet')
    return compute_similarity(image_name, model)

def compute_similarity(image_name, model):
    img_dir = 'images'
    img_id = 0
    print('compute_similarity for image', image_name)
    feature_vectors: dict = {}
    for i, img_path in enumerate(get_all_images_in_dir(img_dir, True)):
            feature_vectors[img_path] = predict(img_path,model)[0]

    results=findDifferences(feature_vectors, image_name)
    print(results)
    return results