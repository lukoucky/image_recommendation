FROM tensorflow/tensorflow:2.3.0

ADD requirements.txt /home/backend/
WORKDIR /home/backend/

RUN pip3 install -r requirements.txt
RUN apt update
RUN apt install -y libgl1-mesa-glx
RUN apt install -y wget

ADD ./backend /home/backend/
WORKDIR /home/backend/

RUN wget https://github.com/matterport/Mask_RCNN/releases/download/v2.0/mask_rcnn_coco.h5

EXPOSE 5555
EXPOSE 8888

ENTRYPOINT ["python3", "app.py"]
