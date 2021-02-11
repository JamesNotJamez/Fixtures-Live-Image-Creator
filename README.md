# Fixtures Live Image Creator

Fixtures live is a ...
This project

## Containers
Provides an isolated environment for the installation of chrome and chrome drivers without having to worry about any conflicts with existing packages on your machine. I've used docker, but other container engines are avaiable 🙂

The Dockerfile has 3 main processes

##### Installing Drivers
The initial large run block handles the installing of chrome and chrome drivers.
> If you're running this in the future, you may need to check that the latest chrome stable release is compatible with the chromedriver version in use.

##### Installing Python Dependencies
Copying in and installing python dependencies before we copy in app source code increases the number of layer hash matches we'll get, and means we don't have to redownload all these dependencies every time we update some code in the app. These dependencies are only redownloaded when there is a new python requirement or a change in a higher level layer.

##### Copying in the source code

## Volumes

*/output* - **directory** - This is where the images are going to be saved

*/TeamMap.yml* - **File** - This YAML file contains a map of the team name as it appears in Fixtures live to how you want it to appear in your image. 

*/this_weeks_teams.yml* - **File** - This contains a list of the teams you want to include in the image, one of the few parts of the process that I'm yet to automate. 

> It is needed for the case the a team was not playing this week but their results are still visible from last weeks games.

## Environment Variables
The app will look fort 


<img width="600" alt="Image Template" src="templates/Brad1.png">


