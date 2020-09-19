FROM python:3.7-stretch
# working directory
WORKDIR /app

# install requirements
COPY ./requirements.txt /app
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

ADD ./wonderline_app /app/wonderline_app
COPY ./gunicorn_config.py /app
COPY ./config.yml /app

# make port 8000 available to the world outside
EXPOSE 8000
# EXPOSE 9000

# create a temporary folder for saving image before moving into minio
RUN mkdir image_tmp

CMD ["gunicorn", "--config", "gunicorn_config.py", "wonderline_app:APP"]