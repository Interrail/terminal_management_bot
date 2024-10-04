FROM python:3.12-slim

# Install required packages for locales
RUN apt-get update && apt-get install -y locales
RUN apt-get update && apt-get install -y locales
RUN locale-gen ru_RU.UTF-8
ENV LANG ru_RU.UTF-8
ENV LANGUAGE ru_RU:ru
ENV LC_ALL ru_RU.UTF-8

# Continue with the rest of your Docker setup
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .


CMD [ "python3", "bot.py" ]