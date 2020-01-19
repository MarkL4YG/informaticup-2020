
# Informaticup2020 Pandemie-Solution

## 1. Group members
* Tim Gurke  
* Torge Hamann  
* Magnus Leßmann  
* Malte Zietlow  

## 2. Running this application  
This application is written in python and can be started either directly from the command line or from the provided docker image.

### 2.1 Configuration and environment
The application port can be changed by setting the ``SERVER_PORT`` variable to a non restricted, unused port number.  
The application comes with several approaches located in ``docker/python/approaches``.
The ``APPROACH`` environment variable can be used to select one of them. Its value must be the file name without extension (``<approach-name>.py``). If no approach has been set, the ``random`` approach is used.  
 
Environment variables work for both the command line and the docker image, when passed.

#### List of available approaches
* ``none`` -> Instantly ends rounds without any other action. (For comparision purposes)  
* ``random_approach`` -> Selects a random action from the list of available ones.  
* ``medication`` -> Immediately tries to develop and deploy medication to infected cities.  
* ``vaccine`` -> Immediately tries to develop and deploy vaccines to infected cities.  
* ``medication_and_vaccine`` -> Combination of the ``medication`` and ``vaccine`` approaches.  
* ``ml_a2c`` -> Advantage Actor Critic-Agent
* ``ml_ppo`` -> Proximal Policy Optimization-Agent
*


### 2.2 Running via. Docker (Preferred)
The Docker image ``markl4yg/informaticup-2020:latest`` can be used to spin up a standalone server that will answer requests from the ``ic20`` test application on ``http://<container-address>:<server-port>/``.  
  
Building the image can be performed from ``<repository>/docker`` by running ``docker build . --file Dockerfile --tag markl4yg/informaticup-2020:latest``. However, this will not be required when the docker hub registry is available.

### 2.3 Running via. command line
From the directory: ``<repository>/docker/python``, the application can be started by invoking ``python3 main.py``.  

