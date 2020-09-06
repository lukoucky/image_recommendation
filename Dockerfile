FROM tensorflow/tensorflow:2.3.0

ADD requirements.txt /home/backend/
ADD get_data.sh /home/backend/

WORKDIR /home/backend/

RUN pip3 install -r requirements.txt
RUN apt update
RUN apt install -y libgl1-mesa-glx
RUN apt install -y wget
RUN apt install -y unzip

RUN ./get_data.sh

EXPOSE 5555
EXPOSE 8888

ENTRYPOINT ["python3", "app.py"]
