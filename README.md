# Application Monitoring with Prometheus and Grafana 

## Steps of Monitoring

1. Expose Metrics
    1. Define own Metrics with client library
    2. Use Exporters
        1. Node Exporter: hardware and OS metrics exposed by *NIX kernels
        2. Blackbox Exporter: allows black box probing of endpoints over HTTP, HTTPS, DNS, TCP and ICMP
        3. cAdvisor Exporter: exposes metrics of containers
2. Expose Logs with Promtail Agent
3. Collect metrics with Prometheus
4. Collect logs with Grafana Loki
5. Visualize with Grafana
6. Alerting through Prometheus Alertmanager

## Build and Run Monitoring System (local)

1. cd into folder "monitoring_services""
2. run: docker-compose up 

# Access Prometheus and Metrics
<br> http://localhost:9090/graph
<br> http://localhost:9090/metrics

# Login into Grafana 

<br> (Default Credentials)
<br> username: admin
<br> password: admin

## Build and Run Example App (local)

1. Build App images: 
    docker build -t andelas/test_app -f  Dockerfile . 
2. Start Containers:
    docker-compose up

# Configuration der E-Mail Benachrichtigung

## Mail Server
Daimler Mail Host Server
- No credentials needed
- NO FW clearance needed within EDC

```yml
mail:
    host: mailhost.emea.svc.corpintra.net
    port: 25

```

## Alertmanager in Prometheus (GMail)

Eingabe der GMail Credentials in der Datei emai-alertmanager.yml

```yml 
global:
 resolve_timeout: 1m

route:
 receiver: 'email-notifications'

receivers:
- name: 'email-notifications'
  email_configs:
  - to: example@gmail.com
    from: example@gmail.com
    smarthost: smtp.gmail.com:587
    auth_username: max_mustermann@gmail.com
    auth_identity: max_mustermann@gmail.com
    auth_password: password
    send_resolved: true
```


