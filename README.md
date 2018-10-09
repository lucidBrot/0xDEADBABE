# Viscon 2018 Project

This is the state of team 0xDEADBABE's submission at the first ever VisCon.  
It is a tool for evaluating teaching assistants, and consists of
* A Postgresql database (not included)
* A Python Flask Webserver as backend
* A frontend in javascript

The main reason why this repository exists is that we can later find our code again with ease if we ever need some guidance for a similar project.  

I like about the backend that
* It generates static html pages for the frontend that contain dynamic content, using jinja
* It handles login with nethz using the people api (which probably doesn't work anywhere except on the VIS infrastructure)
* It uses decorators to prevent users from accessing pages they shouldn't, quite easily (thanks Joshi!)

**Staging:** [![pipeline status](https://gitlab.vis.ethz.ch/viscon-2018/team8/project/badges/staging/pipeline.svg)](https://gitlab.vis.ethz.ch/viscon-2018/team8/project/commits/staging)
