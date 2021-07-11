FROM ubuntu:18.04

COPY requirements.txt /TableDetectionProject/requirements.txt

RUN apt-get update
RUN apt-get install -y --no-install-recommends --yes python3-dev
RUN apt-get install -y --no-install-recommends --yes python3-opencv
RUN apt-get install -y --no-install-recommends --yes python3-setuptools
RUN apt-get install -y --no-install-recommends --yes python3-pip

RUN python3 -m pip install --upgrade pip

WORKDIR TableDetectionProject
RUN pip3 install -r requirements.txt

COPY . /TableDetectionProject

CMD ["/bin/bash", "entrypoint.sh"]
