from keras.applications.resnet50 import ResNet50
from keras.preprocessing import image
from keras.applications.resnet50 import preprocess_input, decode_predictions
from keras.models import Model
import numpy as np
from os.path import join
from utils import is_image, get_all_images_in_dir

resnet50_model = ResNet50(weights='imagenet')

def predict(img_path : str, model: Model):
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    print('Predicting image', img_path)
    return model.predict(x)

def predict_resnet50(img_path: str):
    return predict(img_path, resnet50_model)

def findDifference(f1, f2):
    return np.linalg.norm(f1-np.array(f2))

def findDifferences(feature_vectors, image_name):
    similar: dict = {}
    for k, v in feature_vectors.items():
        diff=findDifference(feature_vectors[k],feature_vectors[image_name])
        similar[k] = diff
    return similar 

def compute_similarity(image_name):
    img_dir = 'images'
    img_id = 0
    print('compute_similarity for image', image_name)
    feature_vectors: dict = {}
    model = ResNet50(weights='imagenet')
    for i, img_path in enumerate(get_all_images_in_dir(img_dir)):
            feature_vectors[img_path] = predict(join(img_dir,img_path),model)[0]

    results=findDifferences(feature_vectors, image_name)
    print(results)
    return results
    # for k,v in results.items():
    #     print(k +" is most similar to: "+ v)    
    # #print('Predicted:', decode_predictions(preds, top=3)[0])

