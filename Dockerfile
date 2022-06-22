# Set base image
FROM ubuntu:20.04
RUN apt-get -y upgrade && apt-get -y update && apt-get -y install python3.9 && apt-get -y install sudo
RUN apt -y install python3.9-venv python3-wheel vim

ENV FLASK_APP flasky.py
ENV FLASK_CONFIG docker

#RUN useradd -m docker && echo "aldo:test123" | chpasswd && adduser aldo sudo
RUN useradd -m aldo && adduser aldo sudo
RUN passwd --delete aldo
USER aldo
# Where the application will be installed
WORKDIR /home/flasky

# Copy requirements folder to WORKDIR
COPY requirements requirements
# Create venv in WORKDIR
RUN sudo python3.9 -m venv venv
RUN sudo venv/bin/pip install wheel 
# Install requirements
RUN sudo venv/bin/pip install -r requirements/prod.txt

COPY app app
COPY migrations migrations
RUN sudo chmod 757 app/
COPY flasky.py config.py boot.sh ./

# run-time configuration
# Map port to host machine
EXPOSE 5000
ENTRYPOINT ["sh","./boot.sh"]
