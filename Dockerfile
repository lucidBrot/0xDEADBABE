# @Author       Eric Mink <minker@vis.ethz.ch>
#
# Test project

FROM registry.vis.ethz.ch/public/vis-base:bravo

RUN apt-get update && apt-get install --no-install-recommends python3

WORKDIR /app/webserver

COPY webserver/requirements.txt .

RUN pip install -r requirements.txt

COPY webserver /app/webserver

EXPOSE 80
CMD ["python", "server.py"]
