from flask import Flask, Response
from flask.globals import request
from prometheus_client import Counter, generate_latest, Summary, Gauge
import time
import random
from loguru import logger
import docker
import sys

# 1. App Analysieren
# 2. Last durch Prometheus Server Analysieren
#    -> ins Verhältnis zur Last der eigentlichen Anwendung stellen (Prometheus Container Monitoren)

def create_app():
    """create_app
    Create a flask app object whicht implements a WSGI application

    Returns:
        flask.Flask : app object
    """
    app = Flask(__name__)

    # config logger
    # logger.remove(0)  # remove deafault logger (useful for development)
    logger.add("log/file_{time}.log", retention="1 days")
    
    
    return app


client = docker.from_env(version='1.41') 
app = create_app()
CONTENT_TYPE_LATEST = str('text/plain; version=0.0.4; charset=utf-8')

# Defining Metrics
SCRAPING_METRICS_COUNTER = Counter('scraping_metrics_counter', 'Counts prometheus scraping metrics.')
REQUEST_COUNT = Counter('request_count', 'App Request Count',['app_name', 'method', 'endpoint', 'http_status'])
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

memory_gauge = Gauge(
    'memory_usage_mb',
    'Memory Usage of Container in Megabyte.',
    ['name']
)

# ---------------- Requests ----------------
@app.route('/metrics', methods=['GET']) 
def get_data():
    """get data
    Get Request on Metric endpoint monitors how often metrics get scraped.
    
    Returns: 
        Response: Returns all data as plaintext.
    
    """

    SCRAPING_METRICS_COUNTER.inc() # increment counter when endpoint gets scraped
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route('/') 
def count_requests():
    """count_requests
    Counts all request made to root-Route of Flask Server.
    """

    REQUEST_COUNT.labels('web-app', request.method, request.path, 200).inc() # increment counter when endpoint gets scraped
    return "Hello World"

@app.errorhandler(500)
def handle_httpException(error):
    """handle_httpException
    When debug mode disabled

    Args:
        error (int): http response code

    Returns:
        (str): displays server error
    """
    REQUEST_COUNT.labels('web-app', request.method, request.path, error).inc()
    return str(error), 500

@app.route('/fail/')
def test1():
    """test1
    Funtion that gets called on endpoint '/fail/' and throws a server error

    Returns:
        (str): does not get reached, would displays 'fail' 
    """
    a = 1/0
    return "fail" # not reached!


@app.route('/time/')
def pTime():
    """pTime
    Random time execution time

    Returns:
        (str): random execution time
    """
    t = random.randint(1, 5)
    process_request(t)
    return f"Time: {t}"

@REQUEST_TIME.time()
def process_request(t):
    """process_request
    A dummy function that takes some time.
    
    Arguments:
        * t (int): time
    """
    print('Hello world!', file=sys.stdout)
    time.sleep(t)



# ---------------- Memory usage ----------------
MiBFactor = float(1 << 20)
@app.route('/memory/', methods=['GET'])
def get_container_memory():
    """get_data
    returns memory data usage of each container as plain text
    
    1. Gets all the containsers
    2. Opens sudo file for each container and read the memory data
    
    """
    containers = client.containers.list()

    for container in containers:
        name = container.name
        try:
            with open('/docker/memory/{}/memory.usage_in_bytes'.format(container.id), 'r') as memfile: # read memory of container
                memory = memfile.read()
                memory = int(memory) / MiBFactor # calc memory in MB
                memory_gauge.labels(name).set(memory)

        except Exception as e:
            logger.error("Failed to update memory metric. Exception: {}".format(e))

    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST) # returns data as plain text




if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5050) #run flask api
    