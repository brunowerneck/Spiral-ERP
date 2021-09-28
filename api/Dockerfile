FROM python:3.9
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt --no-cache-dir
COPY . /code/
ENV FLASK_APP app
CMD python manage.py run --host=0.0.0.0