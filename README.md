<img src="./README_imgs/header.jpeg" width="100%" />


Imagine many people need to go somewhere (party, conference, ...), some of them have their cars while others don't. 
Imagine that you want to divide the people without a car among the avaliable places of the people who have a car.

Carty helps you find the optimal allocation



https://user-images.githubusercontent.com/20478513/147542471-ee255123-d615-4502-9827-58bc08573c9e.mp4



### How does it work? ###

* Create your profile
* Join a group or create a new one
* Add or modify your data (avaliable places, address of departure)
* Run the simulation (it optimizes the solution for all the people present in the group)
* Check the results


### Tech ###

* Frontend: Kivy, KivyMD
* Backend: python
* Model: python, ortools (deployed on AWS lambda)
* Model APIs: AWS Gateway
* Deploy: Buildozer
