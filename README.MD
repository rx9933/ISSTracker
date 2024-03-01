# International Space Station Tracker

This project analyzes the International Space Station's position and velocity based on data provided by NASA. The program supports Flask and Docker, and returns general information about the ISS and specific parameters about the ISS's location/speed at different time points. 

## Table of Contents:
1. [Folder Contents](#folder-contents) 
2. [Data Source] (#data-source)
3. [Diagram] (#diagram)
4. [Prerequisites] (# prerequisites)
5. [Running Program] (# running-program)
6. [Contributions/Citations] (#contributions/citations)

## Folder Contents:
1. "iss_tracker.py": code that requests data about the ISS's position/velocity based on user's flask commands.
2. "test_iss_tracker.py": contains unit tests for iss_tracker.py. 
3. "requirements.txt": the required versions of python libraries (used in Dockerfile).
4. "Dockerfile": contains instructions for docker to work (building/running program).
5. "docker-compose.yml":  containerized docker commands (for automation purposes).
6. "diagram.png": diagram of program.
7. "README.md": this file, describes functionality of app.

## Data Source

Data is sourced from NASA's public data repository: [NASA ISS Website](https://spotthestation.nasa.gov/trajectory_data.cfm). The xml formatted data is used for this project. 
To directly download the data: [Download NASA ISS XML Data](https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml). 

1. Data tracks the ISS, providing the location (x, y, and z coordinates) and the velocity (in the x, y, and z directions) at different times/epochs.
2. For the xml data type, the epochs are given in the following format: 2024-043T12:00:00.000, where this time represents the 43rd day from January 1st, 2024 (February 12th) at time 12:00:00 p.m. in UTC (Coordinated Universal Time, located in London, England). All times in the data are presented in UTC format.
3. Positional and velocity data is recorded in kilometers (km) and kilometers per second (km/s). 
4. Various statistics about the ISS are also provided (i.e, the mass of the ISS, drag area, drag coefficient, etc.)
5. The start and stop dates of data collection are also provided. 

## Diagram
## Prerequisites
## Running Program

# Contributions/Citations
* Professor Joe Allen: on providing immediate help for all my questions.
* ChatGPT: on writing this README.md.
* [COE 332: Software and Engineering Design Read The Docs](https://coe-332-sp24.readthedocs.io/en/latest/unit05/containers_2.html): on usage (running the program with Linux commands)
* [NASA ISS Website](https://spotthestation.nasa.gov/trajectory_data.cfm): on providing data.