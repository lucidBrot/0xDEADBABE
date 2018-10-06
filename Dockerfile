# @Author       Eric Mink <minker@vis.ethz.ch>
#
# Test project

FROM registry.vis.ethz.ch/public/vis-base:bravo

RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip python3-setuptools

WORKDIR /app/webserver

COPY webserver/requirements.txt .

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt

COPY SQL ../SQL
COPY webserver /app/webserver

EXPOSE 80
CMD ["python3", "server.py"]
