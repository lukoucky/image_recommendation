# Image Similarity

This goal of this project was `to create a solution for finding the most similar content`. This broad assignment left huge space for personal inventions. I have chosen to implement system that outputs set of images similar to the image given as input. Recurrent neural network is used for similarity search. To present working solution this project contains backend Flask application that is connected to database with 5000 image from [COCO dataset](https://cocodataset.org/#home). This web app allows to search through the database, find similar images to random one from the database and also to upload new images to the database and see similar images from the database.

Each section of this readme will guide you step by step through the process of how I implemented the project. You can access github of this project here: [https://github.com/lukoucky/image_recommendation](https://github.com/lukoucky/image_recommendation) and live demo of project running here: [http://lukoucky.com:5555/](http://lukoucky.com:5555/). Please note that the demo is running on my very slow server and for example similarity search for newly uploaded image can take up to a minute. On my CPU however this takes about two seconds and on GPU is this process instant. For best experience run the project locally. All you need to do is to have Docker and Docker-compose installed and run:
```
docker-compose up --build -d   # To run the container.

docker-compose down   # To stop it and remove everything.
```

### Possible problems with running docker:
Sometimes the file `mask_rcnn_coco.h5` containing weights for neural net or dataset with images is not downloaded properly during docker build and docker backend app can't work without them. In case this happens you must download [mask_rcnn_coco.h5](https://github.com/matterport/Mask_RCNN/releases/download/v2.0/mask_rcnn_coco.h5) and place it into `backend` directory. And download [COCO dataset](http://images.cocodataset.org/zips/val2017.zip) and unzip all images into `backend\images` folder. You can also use script `get_data.sh` that will do this for you.

## 1 Research on current solutions

As with any other project the best way to start is to find out how other people do it. I have started with through online research mostly on data science and machine learning blogs, [Github](https://github.com/), [Kaggle](https://www.kaggle.com/) and [Arxiv](https://arxiv.org/). There are a lot of materials for this subject but they very often work only on very limited types of images. You can find nice articles like [this](https://www.oreilly.com/library/view/practical-deep-learning/9781492034858/ch04.html) where authors use output of ResNet-50 neural network as extracted features from image and than use Nearest Neighbor search to find similar images. I have implemented a very similar solution to the one in the article but it shows zero capability for similarity search on images from normal situations. By this I mean images from real life situations like you can find on instagram, facebook or in your phone. This approach is suitable only for simple tasks like deciding if an image is a dog or cat (if you have only images of dogs and cats). 

For better similarity search on real live images was necessary to understand the scene better. Scene understanding is a common computer vision task and many great solutions are available. Many fields study this problem. For example Image classification, Semantic segmentation or Instance segmentation. I have chosen Instance segmentation as promising approach. It's task is to locate instances of objects on image and label them. This seems like a great way to find what is actually on an image and then use this information for similarity search. 

There are many articles about Instance segmentation and several implementations available. For example [InceptionV3](https://arxiv.org/abs/1512.00567) produces great results. But I have chosen [Mask_RCNN](https://github.com/matterport/Mask_RCNN) for this task. It is a recurrent convolutional neural network described in [this article](https://arxiv.org/abs/1703.06870). Together with [PixelLib](https://github.com/ayoolaolafenwa/PixelLib) library it is super easy to load pretrained network, feed it with image and get out with list of objects on image, probability that objects were correctly identified and pixel perfect map of objects. COCO dataset lists 81 different objects. That is why design the feature vector as 81 values from 0 to 1 where each number shows the probability of given image being in the image. Nearest Neighbor search is done on these feature vectors and result is used as system output. This approach produces great results not only on COCO dataset images but also on any most real life images.

Great thing about this solution is it's fast and scalability. Computing a feature vector on a common CPU took about 2 seconds but with GPU this computation is almost instant and there is still some room for improvement. So the only bottleneck could be similarity search on feature vectors. I am now using Nearest Neighbor search which is super fast for a few thousand images but can become a problem for a few million images. But there are fast methods that takes into account such cases. For example [Faiss](https://engineering.fb.com/ml-applications/faiss-a-library-for-efficient-similarity-search/) library can execute search on 1 billion vectors in under 100ms. 

## 2 Architecture

The whole system is designed as a python backend service running in docker. There are two docker services. First is database service running PosgreSQL database only. Database have just one table `image` with three rows - `id` as unique key, `name` with name of image and `feature_vector` with feature vector as array of floats. Second service runs Flask server with similarity search. This service communicates with other systems using REST API. That way it is easy to use it with mobile or web apps. Tow main API endpoints are used, they are:

### /upload_file [POST]
 
Endpoint expects new image in post request. Image is saved on the backend, the feature vector is then computed and saved to the database. Name of the saved image used in the database is sent back in a JSON response.

### /get_similar/<image_name> [GET]

Expects name of image already in database as input. In response returns all images from the database from most similar to least similar paginated be 30 images.

There are also other endpoints serving web pages and static files for web pages. You can find the implementation of backend server in file `backend/app.py`.

## 3 Implementation

As I wrote in section 1, similarity search is done using recurrent convolutional network Mask RCNN. Pretrained weights was taken from [here](https://github.com/matterport/Mask_RCNN/releases/tag/v2.0). Very helpful is [PixelLib](https://github.com/ayoolaolafenwa/PixelLib) library that handles network initialization and prediction. This model is wrapped around simple class located in file `backedend\instance_segmentation_model.py`.

I really like to use Jupyter notebooks during work on any project. This time was no different and you can find some parts of my work in progress in two notebooks `backend\RandomSimilarityWithSegementation.ipynb` (predictions on random images from dataset) and `backend\WorkingNotebook.ipynb` (with some initial implementation of helper classes).

Another interesting code can be found in `backend\dataset.py`. This class serves as a helper for work with a dataset of images. It stores all information about data, loads pickles with precomputed data and so on.

`backend\db_model.py` contains SQLAlchemy model of database.

`backend\image_similarity.py` contains initial work with ResNet-50 features mentioned in the begining.

`app.py` contains a Flask server with all the functionality for similarity search system functionality.

## 4 Deployment

Since the whole system is running in Docker deployment is super easy. All you need to do is clone the
[github repo](https://github.com/lukoucky/image_recommendation) to where you want to use the system and build docker containers. 

For the production would be best to use AWS, Azure, Heroku, Google Cloud or similar service. There you can easily use automated services that handle requests load and spawns new instances of service if needed.

## 5 Conclusion and improvements

I have chosen to implement a service that takes image and search similar images to it from a database. I have also set up a domain of images to be real live pictures. No images with a single object in front of white wall but image people commonly take on their phones. Images are matched based on instance similarity to produce great results.

How to turn this into recommendation engine? As mentioned in previous section it would need to be deployed on reliable and scalable server. API than can be integrated into existing mobile or web application to return similar images on demand. Function like this is implemented on demo web page. You can click on button `Random image` to select random image from database and than click on any of the similar images to go deeper and discover more.

There are also still some places for the system improvement: 
* I am using only object presence for similarity search but there are more information in network output. I am not using location of objects on image and their color for example. Including these informations into feature vector in definitely improve results.
* Used similarity search only recognize 81 different objects on image. If you take a picture of something out of this set system would not work. System would have to be trained to recognize much more objects to be useful in next instagram app. But it is important to know what domain of usage customer demands (do they want another instagram or app to recognize similar car models ...)
* User generated content usually contains some data from user itself - like tags or text description. Including this as another feature would be probably best for improvement. Also users themself could be features - you want to see other pictures from them or similar users.
* Some images could contain text. Run a text recognition on image and using text found there could be another great feature

I have used source code from the following github repos and web pages:
* [Drag and drop to upload file with Flask](https://github.com/pcote/DragDropProject)
* [Flask + PostgreSQL in docker](https://github.com/Azure-Samples/docker-flask-postgres)
* [Deep Learning Image Similarity](https://github.com/dipayan90/deep-learning-image-similarity)
* [PixelLib](https://pixellib.readthedocs.io/en/latest/Image_instance.html)


