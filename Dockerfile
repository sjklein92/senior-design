# deltawhy/chimera
FROM ubuntu:trusty
RUN apt-get update && apt-get install -y --no-install-recommends\
    build-essential\
    couchdb\
    git\
    libv8-dev\
    python\
    python-pip\
    ruby2.0\
    ruby2.0-dev
RUN sed -i 's/127\.0\.0\.1/0.0.0.0/' /etc/couchdb/default.ini &&\
    install -o couchdb -g couchdb -d /var/run/couchdb &&\
    gem2.0 install jekyll therubyracer

COPY requirements.txt /
RUN pip install -r /requirements.txt
COPY . /app

EXPOSE 8080 5984
VOLUME ["/data","/app/instance","/var/lib/couchdb"]
WORKDIR /app
CMD couchdb -b && sleep 1 && python run.py
