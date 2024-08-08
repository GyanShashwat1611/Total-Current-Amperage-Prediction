# Total-Current-Amperage-Prediction

### The report of data anlysis and model training is in the report directory.
```
cd Report
``` 
- The report is html file contains all the codes and output of the jupyter notebook used for data analysis and development of the model.
- There is one slides.html file which contains presentation of the outputs and the outcomes of the report as well, please have a look.

### The ipython notebook and trained model is also saved in the project direcctory so that it can be used easly. 

### The POC is created in Flask and has a folder structure, it is containerized in the docker for easyy installation.

## Getting Started
These instructions will get you a copy of the project up and running on your local machine. I have also mentioned the process which we follow for deploying an application on the aws server using CI/CD github actions and docker container

## Prerequisites
What things you need to install the software and how to install them

```
Python>=3.10
pipenv or virtualenv
WSL (if on Windows)
Docker & docker-compose
requiremnts.txt
```
##  Environments

Please find installation instructions and instructions on how to run the
respective environments below using Docker.

- [On Server](#ServerInstallation )
- [Locally (Windows/WSL or Ubuntu)](#local_docker)
<a name="ServerInstallation"><h2>Developing on Server</h2></a>
1) Create a release using CI/CD github actions for the repository.
2) Push the release to the AWS ECR 
3) Deploy the docker container on the ECR by pusing new image using docker-compose yml file.


<a name="local_docker"><h2>Developing locally with Docker (Windows/WSL or Ubuntu)</h2></a>

> Please download the `latest version` of Ubuntu when installing it for the first time.

_For Ubuntu skip steps 1-4_

1) Install Docker from [Docker Hub](https://hub.docker.com/editions/community/docker-ce-desktop-windows/)

2) Install WSL (Windows Subsystem for Linux) - [Instructions here](
  https://docs.microsoft.com/en-us/windows/wsl/install-win10)

3) Make sure WSL version 2 is used and enabled on Docker Desktop - [
  Instructions here](https://docs.docker.com/docker-for-windows/wsl/)

4) Open WSL terminal from PowerShell (or another terminal) with the following
command
    ```
    wsl.exe
    ```

5) Update ubuntu packages and install packages
    ```
    sudo apt-get install git python3 python3-pip -y
    ```

6) Unzip the project zip file 
    ```
    unzip [FileName].zip
    ```

7) Install `docker-ce` - [Instructions here](
  https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-22-04)


8) Once doker is installed, check by command.
```
docker ps
```

9) Build Total-Current-Amperage-Prediction Docker image by using Dockerfile
    ```
    docker build . -t app
    ```

10) Run docker containers locally
    ```
    docker run -p 5000:5000 app
    
    ```
11) Once the app will start runninng the url will be exposed and can render the view.


