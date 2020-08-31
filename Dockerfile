FROM alpine:3.12

ADD requirements.txt /home/backend/
WORKDIR /home/backend/

RUN apk add --no-cache postgresql-dev gcc python3 python3-dev musl-dev && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    rm -r /root/.cache && \
    pip3 install -r requirements.txt

ADD ./backend /home/backend/
WORKDIR /home/backend/

EXPOSE 5555

ENTRYPOINT ["python3", "app.py"]
