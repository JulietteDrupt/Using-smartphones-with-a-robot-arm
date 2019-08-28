# Enabling a robot arm to use Android apps using images of the screen

The aim of this project is to generate test scenarios for Android apps using only images of the smartphone's screen, and to execute such scenarios with a robot arm holding a stylus. I filmed the screen with a FLIR Flea3 USB3 camera and used a DOBOT Magician robot arm. The project is written in Python.
I worked on this project during a 3-month internship at *Polytechnique Montréal*. I re-used the previous work of other students who used the source code of Android apps instead of images from the screen to determine apps'content and generate scenarios.

There are still many things to improve but this may help someone with a similar project to get started. This project may also help someone willing to process images from a FLIR camera with Python.

## Getting Started

This project was developped with Ubuntu 18.04, but you should be able to use use it with Windows or MacOS after installing the same Python libraries and the drivers that correspond to your OS.

### Prerequisites

You will need **OpenCV 4**.

Linux:
```
sudo pip install opencv-python
```
You will also need to install the drivers for FLIR FLea3 USB3 camera. Download first **Spinnaker** and **Python-Spinnaker** from [FLIR's official website](https://www.flir.com/products/spinnaker-sdk/) and follow the installation instructions.

DOBOT Magician's dlls are already provided in folder *FLIR-Flea3-USB3-and-DOBOT-Magician-Smartphone-Tester/ressources/dlls*.

### Installing

Download project:

```
git clone https://github.com/JulietteDrupt/Using-smartphones-with-a-robot-arm.git
```

## Contents

### FLIR-Flea3-USB3-Image-Aquisition

This folder contains Python scripts to acquire images from FLIR Flea3 USB3 camera.

* display-video.py displays current images as a video until you exit by pressing 'q'.
* take-picture.py saves current image in a file called 'camera.png'.

### FLIR-Flea3-USB3-and-DOBOT-Magician-Smartphone-Tester

This folder contains DOBOT Magician's dll and all the programs that use this robot, each sub-folder corresponding to a different approach. I assume the camera can see your entire screen and the robot can acces to any part of your screen with no need to move the camera. Make sure you do not move your phone after launching any program.
Follow the instructions that will appear after launching any program.

All sub-folders contain:
* **DobotDllType**: this libray is provided by DOBOT and allows to connect and control DOBOT Magician using the correct dll. It is the same in each sub-folder.
* **Dobotfunctions**: this library was developped by another student who worked on using DOBOT Magician to test Android apps. It contains the functions used to interact with a touch-screen, such as *Movement*, *Touch*, *Scroll*... It is the same in each sub-folder.
* **screen**: this library allows to calibrate DOBOT Magician given the position of some points of interest on the screen. It then allows to convert the position of any object from the screen's basis to the robot's basis. It is the same file in each sub-folder.
* **Camfunctions**: this library contains all the functions I wrote to acquire images of the screen with FLIR Flea3 USB3 camera and process them in order to generate or execute some scenarios. **This file is different from a sub-folder to another**, as these functions can be very different depending on the approach.

**Calibration image**: This folder also contains the image required to calibrate DOBOT Magician and FLIR camera to use them together: *calibration-image.jpg*. **Resize it or reproduce it with the dimensions of your phone's screen, and download it on your phone**. Each red dot must be located in a corner of your phone's screen when displaying it. Having this image the good size is very important because it is also used to locate the screen and get its dimensions.

#### Green-dots-test
This folder's files allows to test whether the coordinates of an object in the screen are well-converted to the robot's basis. It is also the most basic program in this project using both DOBOT Magician and FLIR FLea3 camera, so having a look at it may be a good start.

Before launching the main, **download *dots.png* on your phone, display it and zoom** as much as you can to still have the 4 dots on your screen. Then, follow the instructions.

When pressing 'c', the dots' positions in the image are detected and send to the main after disconnecting the camera by pressing 'q'. The red dots are then used to calibrate the robot arm, what allows to convert the coordinates of the green one to the robot's basis. The robot will then touch it.

#### Find-buttons-for-Samsung-Calculator-10.0.02.3

The objective here was to segment the image of a precise calculator app - Samsung Calculator 10.0.02.3 - and thus detect the main buttons of the calculator and their position. The robot could then touch them one by one.
As it is really specific to this app, such program might not have a huge interest depending on your phone.

The image of the screen is segmented in order to retrieve its main buttons and their position. Disconnecting the camera launches robot's calibration, then the position of the objects detected are converted to the robot's basis and it touches them one by one.

### Find-objects-with-single-capture

This folder's files allow to take a picture of the screen and detect most graphical objects in this screen using a segmentation algorithm (quite similar to the previous, but more general).

* testWithoutDobot.py: DOBOT Magician needn't to be connected, and the objects detected are just displayed.
* main.py: DOBOT Magician must be connected. After disconnected the camera, the robot is calibrated and then touches all the objects detected.

Here, graphical object detection with segmentation is limited to one single image of the screen, so it cannot generate any scenario.

### Random-scenarios-with-multiple-captures

In this case, the graphical objects are detected with the same segmentation algorithm as in *Find-objects-with-single-capture*, but there are some important differences from *Find-objects-with-single-capture* :
1. DOBOT Magician is called in the same loop as the camera, so its action is not limited to a single screen image;
2. The robot doesn't touch all the objects detected but picks one randomly;
3. Before being segmented, any image of the screen is compared to the previous one to be segmented. If they look similar, the algorithm looks for regions that may have changed between them, for instance some buttons, a window or a keyboard, ie any object that mays have popped up. In case such different regions are detected, the next object to be touched will be necessarily located in these regions.

All comparision functions are in *ImComparison.py*.

### Pre-written-scenarios

The idea here is to compare the image of the screen to a database of screenshots and launch a scenario that corresponds to the identified screen.

*WriteScenario.py* displays the image of the screen on a window. You can generate manually a scenario by clicking on the area of the screen you want the robot to touch. You can indicate to scroll a similar way.

When writing a scenario, you will be asked to choose a filename: it should be saved in sub-folder *Scenarios/Scenarios*. Also save a screenshot of the screen that must be displayed to launch your scenario, in sub-folder *Scenarios/Images*. Depending on the number of scenarios you would like to work with and the names of scenario files and corresponding screenshots, you will have to modify file *Scenarios.py*.

*ChooseDemo.ipynb* shows examples of comparisons between images of the screen and screenshots.

### Keyboard-detection

Here, when pressing 'y', the program compares the image of the screen to the one of your keyboard. I the keyboard is detected, it writes "hello world" (I have an azerty keyboard so it may not write exactly "hello world" on yours).

Make sure you save a capture of your own keyboard as *clavier.jpg* before running *main.py*. You should also modify *hello* tab in *helloCoord* function in *Camfunctions* with the coordinates of 'h', 'e', 'l', 'l', 'o', space, 'w', 'o', 'r', 'l', 'd' in your keyboard image. You can run *hello.py* to get these coordinates and print them in the console.

