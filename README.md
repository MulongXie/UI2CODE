# UI2CODE - A Computer Vision Based Reverse Engineering of Graphical User Interface

> This project is still ongoing, while the UI element detection part is useable and can be download in [this repo of UIED](https://github.com/MulongXie/UIED.git). Besides, I implemented a web app of GUI element detection based on our algorithm, you are welcome to have a try http://www.uied.online.

## What is it?

UI2CODE is a system converting the GUI image into cooresponding front-end code that achieves the same visual effect and expected functionality of the input GUI.

It comprises two major parts: 
* UI components detection: localize and classify all UI elements on the given image
  * Graphical components detection 
  * Text recognition through [EAST](https://github.com/argman/EAST) 
* Code generation
  * Repititive component recognition
  * DOM tree construction
  * HTML + CSS generation

![UI Components detection result](https://github.com/MulongXie/UI2CODE/blob/master/Element-Detection/data/demo/demo.png)
