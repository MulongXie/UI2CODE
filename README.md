# UI2CODE - A Computer Vision Based Reverse Engineering of Graphical User Interface

## What is it?

UI2CODE is a system converting the GUI image into cooresponding front-end code that achieves the same visual effect and expected functionality of the input GUI.

It comprises two major parts: 
* UI components detection: localize and classify all UI elements on the given image
  * Graphical components detection 
  * Text recognition through CTPN 
* Code generation
  * DOM tree construction
  * HTML + CSS generation

## Demo
![UI Components detection result](https://github.com/MulongXie/UI2CODE/blob/master/demo/uied.png)
