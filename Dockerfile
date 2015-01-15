# This is a comment
FROM ubuntu:14.04
MAINTAINER Michael MacKinnon <mike@eth0.ca>
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y python3-setuptools
RUN easy_install3 pip
RUN apt-get install -y libpq-dev python3-dev
ADD . /app
RUN cd /app ; pip install -r requirements.txt
EXPOSE 5000
WORKDIR /app
# For now we serve static assets over our WSGI server so we must collect static assets
CMD ["python3", "manage.py", "collectstatic", "--noinput"]
CMD ["waitress-serve", "--port=5000", "shiftgap.wsgi:application"]
