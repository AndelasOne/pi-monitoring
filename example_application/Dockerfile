FROM python:3.8.3-slim

RUN apt-get update && apt-get install -y python3-tk
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY . /


ENTRYPOINT ["python"]
EXPOSE 5050
CMD ["/test-app.py"]