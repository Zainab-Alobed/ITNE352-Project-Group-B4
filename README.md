# Multithreaded News Client/Server Information System

## Project Description
The Multithreaded News Client/Server is a simple Information System that aims to enable a secure exchange of information about recent news between clients and the server. 
The server retrieves the news from https://newsapi.org/ depending on the client's request, where it can manage the connection with multiple clients in the same time.
However, the system provides the user with a menu so it can choose between headlines and sources easily and provide a detailed response if required.

## Semester
S1 2024-2025

## Group
**Group name**: B4
**Course Code:** ITNE352  
**Section:** 02  
**Students:**
- Israa Isa Ahmed Altaitoon (ID: 202206492)  
- Zainab Hasan Isa Alobed (ID: 202206986)

## Table of Contents
1. [Title](#multithreaded-news-clientserver-information-system)
2. [Project Description](#Project-Description)
3. [Semester](#semester)
4. [Group](#group)
5. [Requirements](#requirements)
6. [How to](#how-to-run-the-system)
7. [The Scripts](#the-scripts)
8. [Additional Concepts](#additional-concepts)
9. [Acknowledgments](#acknowledgments)
10. [Conclusion](#conclusion)
11. [Resources](#resources)

## Requirements
Follow these steps to set up the project locally:

1) Clone the repository:  
   ```bash
   git clone https://github.com/Zainab-Alobed/ITNE352-Project-Group-B4

2) Install required libraries:
    pip install -r required.txt

3) Run the server.py

4) Run the client.py

## How to run the system:
**Run the server:**

1) Navigate to the server directory:
    cd server

2) Start the server:
    python server.py

**Run the client:**

1) Navigate to the client directory:
    cd client

2) Start the client:
    python client.py

**Interacting with the server:**

1) The user will be asked about his name, and send it to the server

2) The main menu will be displayed in client side that contains three options:

1. Headlines 
2. Sources
3. Quit

the user must input a valid number 1-3

3) A submenu of either headlines or sources will be displayed depending on the user choice

4) Later on, a maximum of 15 article will be displayed to provide the user the ability to request detailed information or go back to the main menu (Each request will be directly send to the server and print the response back in the client side)

5) The user can select (3) Quit to terminate the program

# The scripts

**Client script**

**Server script**

# Additional Concepts

# Acknowledgments
We would like to thank our instructor for providing this project so we can learn how to implement a python network system.
Moreover, a big think to NewsAPI for providing the news.

# Conclusion
This project demonstrates how secure connections, API integration, Sockects, and client-server communication can be practically implemented using a Python network application.

The development of the Multithreaded News Client/Server Information System helped us learn concepts of: 
- Network programming (Python)
- API integration
- Multi-threaded
- client\server framework

# Resources
- API: https://newsapi.org/








