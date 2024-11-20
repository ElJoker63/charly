FROM python:3.9.16-bullseye

RUN mkdir /app
WORKDIR /app
RUN chmod +777 /app
COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN mkdir uploads
