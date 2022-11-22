FROM python:3.10.4-bullseye
COPY ./app /app
WORKDIR /app
RUN echo 'deb http://deb.debian.org/debian/ bullseye main contrib non-free' >> /etc/apt/sources.list
RUN echo 'deb-src http://deb.debian.org/debian/ bullseye main contrib non-free' >> /etc/apt/sources.list
RUN apt-get -y update && apt-get -y upgrade
RUN apt-get -y install libcairo2-dev fontconfig ttf-mscorefonts-installer
RUN fc-cache -f -v && rm -rf /var/cache/*
RUN pip install -r requirements.txt
CMD ["python",  "./main.py"]