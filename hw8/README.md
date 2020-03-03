# Homework 8: 
## Part 1: Image Annotation
For this homework, you will be annotating the Millennium Falcon and TIE Fighters in images from Star Wars: The Force Awakens.  

The Millennium Falcon

![Image of the Millennium Falcon](./falcon.jpg)


Three TIE Fighters

![Image of the Millennium Falcon](./fighters.jpg)


Annotations for an image include the object coordinates and the corresponding label or class.
For example, an image with two TIE Fighters will have an annotation similar to:

```xml
<annotation>
    <folder>images</folder>
    <filename>image1.jpg</filename>
    <size>
        <width>1000</width>
        <height>563</height>
    </size>
    <segmented>0</segmented>
    <object>
        <name>Tie Fighter</name>
        <bndbox>
            <xmin>112</xmin>
            <ymin>281</ymin>
            <xmax>122</xmax>
            <ymax>291</ymax>
        </bndbox>
    </object>
    <object>
        <name>Tie Fighter</name>
        <bndbox>
            <xmin>87</xmin>
            <ymin>260</ymin>
            <xmax>95</xmax>
            <ymax>268</ymax>
        </bndbox>
    </object>
</annotation>

```
Spending no more than 3 hours, annotate images, identifying the Millennium Falcon and TIE Fighters.   You will want to use an image tool such as labelImg (https://github.com/tzutalin/labelImg) or RectLabel (macOS only, available in the App Store) and export the annotations in the PASCAL VOC format.  As this requires the user of a user interface, it is recommended that your normal workstation be used.

Images should be annotated with the following rules:

* Rule 1: Include all visible part and draw as tightly as possible.
* Rule 2: If multiple instances, label all instances.
* Rule 3: Occluded parts do not matter as long as all visible parts are included.

Steps (Assuming labelImg):
1. Install the tool, following the steps on https://github.com/tzutalin/labelImg
2. Clone the repository https://github.com/rdejana/MIDS_HW8 into a working directory, e.g. /Users/rdejana/Documents/Homework.  In the subdirectory IDS_HW8/images/, you'll find the images that you'll be annotating.  
3. Create a directory that'll be used to store the annotations, for example /Users/rdejana/Documents/Homework/MIDS_HW8/annotations.
4. Start lalbeImg
5. Click "Open Dir" and select the images directory, e.g. Users/rdejana/Documents/Homework/MIDS_HW8/images
6. Make sure that PascalVOC is displayed under the "Save" icon.
7. Click "Change Save Dir" and set it to your annonations directory.
8. Start annotating.  Select "Create RectBox" and draw the bounds around any instances of Millennium Falcon or TIE Fighers you see in the image, adding the correct label.  When done with an image, press "Save".  Continue on to the next image repeating the process until complete or your reach the time limit.


Questions: 
1.	In the time allowed, how many images did you annotate? *All of them, 384 in about 2hours 40 mins. This was aided by turning on the Autosave feature, using keyboard shortcuts and labelling all the TIE Fighters of a bunch of images and then going back and doing the Millennium Falcons. I also did it in 20-30 minutues bursts to prevent fatigue*
2.	Home many instances of the Millennium Falcon did you annotate? *311 Millennium Falcons* How many TIE Fighters? *304 Tie fighters. The count was using the following code:* `grep -roh TIE . |wc -w`
3.	Based on this experience,  how would you handle the annotation of large image data set? *I would not attempt to label a large dataset by hand on my own. There are several available options, the preference for which would depend on the project att hand. I th labelling was for a generic object that most people can recognise, crowdsourcing through Mechanical Turk or similar is a goo optio. However, to couteract accuracy issues I would get each image labelled by several different users and remove obvious error. Another method would be to label a smaller dataset and use machine learning technique to label similar pictures. Then I would implement manual checking and algorithm refinement. If it was a specialist dataset for a cmpany or client, I would be more likely to consider in-house labelling. This does have a higher cost, but it ay be the only option in some cases. Finally, there is the option of using specialist label service companies. This would be a good choice if accuracy and/or the level of difficulty was reasonably high.*
4.	Think about image augmentation?  How would augmentations such as flip, rotation, scale, cropping, and translation effect the annotations? *These types of augmentation do not fundamentally chnage where the item of interest is so the annonations would not need to be repeated. However, the same mathematical transform that is applied to the image must also be applied to the annotation as the x and y coordinates of the rectangle will morph.*

## Part 2: Image Augmentation
For part 2, you will need to install docker in a VM or your local workstation.  

1. Run the command:
```bash
       docker run -d -p 8888:8888 ryandejana/hw8augmentation
```
2. If using a VM, open your browser to ```http://<<yourPublicIP>>:8888/notebooks/augmentation.ipynb``` or if local, ```http://127.0.0.1:8888/notebooks/augmentation.ipynb``` and login with the password ```root```.
3. Run the notebook.

If you wish to experiment with the augmenation library, see https://github.com/codebox/image_augmentor

Questions: 
1. Describe the following augmentations in your own words
-	Flip -*Mirror the image across an axis - usually the horizontal or vertical direction*
- 	Rotation -*Shift the image around the centre point. Usually 90 or 270 degree rotation.*
-	Scale - *Change the number of pixels that capture the image data.*
-	Crop - *Zoom into a section of the image and extract.*
-	Translation - *Skew an image along different axes*
-	Noise - *Add random changes to pixels in the image. This could be in the form of selective colouring or just brightening/darkening certain areas. Other forms of noise include moving pixels a certain distance from their original location.*

## Part 3: Audio Annotation
Take a look at and explore the audio annotation tool CrowdCurio https://github.com/CrowdCurio/audio-annotator)

Questions:
1.	Image annotations require the coordinates of the objects and their classes; in your option, what is needed for an audio annotation? *For complex audio of things such as city noise, audio annotation requires the class and the start and finish time of the audio class in the clip. Additional information such as quality (background noise present, distance from target) may increase the ability of the model to operate in varied environments when trained on a variety of qualities. For speech, many models can cope with a slightly looser approach, such as the words contained in a 3-6 second clip. Speech is punctuated through silences which the model can use to distinguish words. City soundscapes (or other similar audio annotations in the wider environment) may not have quiet periods between sounds to help the ML model create the distinction.*

## What to turn  in
### Part 1
1. A zip or tar file of your annoations. *See https://github.com/stephmather/w251/blob/master/hw8/annotations.zip*
2. Your answers to questions 1 through 4. *See above*

### Part 2
1. Your answer to question 1. *See above*

### Part 3
1. Your answer to question 1. *See above*

