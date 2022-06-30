# Notes on CICD

## About deploy_service_on_server:

- It pulls the blogging docker image from dockerhub, build and runs it there
- Since the image also needs to talk to a mysql server docker image, the mysql docker image needs to be built with the blogging image. This is done by the docker-compose.yml, which takes in secrets from .env-flasky and .env-mysql
- Therefore, these files need to be copied manually to the server. Copy it to the location specified in the CD.yml. Remember to update it in the server if changed
- About ssh to the server, there are two ways to ssh to the server. 
  - The first way is to generate a public key on a client, and copying that public key to authorized_keys of 
    the server.
  - The second way is to generate a public-private key pair in the server, put the public key to the server's authorized_keys, and copy the private key to the client's ssh folder.
  - In the CD we use this second way. More info here: https://zellwk.com/blog/github-actions-deploy/