# Notes on Docker and debugging

- There are two docker containers, one for the app and other for the database
- Communication between the two is set up in docker-compose.yml, look there for more info
- To build and run both, use ```docker-compose up -d --build```, ```-d``` switch is so the process runs in the background
- The ```mysql``` service does not need to be built because the image is already available from online, the ```up``` command only builds ```flasky```
- To execute commands in ```mysql``` service for debugging, use ```docker exec flasky_mysql_run_b34ccf7846ad mysql --user=aldo --password=mypaSsAL -e 'show databases;'```, where ```-e``` switch is execute command
- To use normal ```mysql``` command to talk to the ```mysql``` service for debugging, use ```mysql -uroot -p123 -h 127.0.0.1 -P5423```

