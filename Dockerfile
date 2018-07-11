FROM ubuntu:18.04
# && apt-get -y install redis-server &&
RUN apt-get update && apt-get -y install tesseract-ocr \
    && apt-get -y install libtesseract-dev \
    && apt-get -y install python \
    && apt-get install -y python-pip
COPY . /src
VOLUME /src
WORKDIR /src
RUN pip install -r requirements.txt