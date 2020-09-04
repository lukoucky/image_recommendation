FROM tensorflow/tensorflow:2.3.0

ADD requirements.txt /home/backend/
WORKDIR /home/backend/

RUN pip3 install -r requirements.txt
RUN apt update
RUN apt install libgl1-mesa-glx

ADD ./backend /home/backend/
WORKDIR /home/backend/

EXPOSE 5555
EXPOSE 8888

ENTRYPOINT ["python3", "app.py"]
