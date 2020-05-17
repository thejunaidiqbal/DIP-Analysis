# -*- coding: utf-8 -*-
"""
Created on Sun May 17 03:21:27 2020

@author: thejunaidiqbal
"""




"""
This program performs grain size distribution analysis and dumps results into a csv excel file.
It uses watershed segmentation for better segmentation.
Compare results to regular segmentation. 
For multiple files.
Better than for loops, just put all code into a function and 
apply the function to multiple images. 
"""

import cv2
import numpy as np
from matplotlib import pyplot as plt
from scipy import ndimage
from skimage import measure, color, io



def grain_segmentation(img):
    

    ret1, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)


    kernel = np.ones((3,3),np.uint8)
    opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 1)



    sure_bg = cv2.dilate(opening,kernel,iterations=2)


    dist_transform = cv2.distanceTransform(opening,cv2.DIST_L2,3)


#print(dist_transform.max()) 
    ret2, sure_fg = cv2.threshold(dist_transform,0.2*dist_transform.max(),255,0)


    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg,sure_fg)


    ret3, markers = cv2.connectedComponents(sure_fg)


    markers = markers+10

    markers[unknown==255] = 0
#plt.imshow(markers)

    markers = cv2.watershed(img1,markers)

    img1[markers == -1] = [0,255,255]  

    #img2 = color.label2rgb(markers, bg_label=0)

    #cv2.imshow('Overlay on original image', img1)
    #cv2.imshow('Colored Grains', img2)
    #cv2.waitKey(0)


    regions = measure.regionprops(markers, intensity_image=img)
    return regions




pixels_to_um = 0.5 # 1 pixel = 500 nm 

propList = ['Area',
            'equivalent_diameter', 
            'orientation', 
            'MajorAxisLength',
            'MinorAxisLength',
            'Perimeter',
            'MinIntensity',
            'MeanIntensity',
            'MaxIntensity']    
    
output_file = open('images/grains/image_measurements2.csv', 'w')
output_file.write('FileName' + "," + 'Grain #'+ "," + "," + ",".join(propList) + '\n') 


import glob

path = "images/grains/*.jpg"
for file in glob.glob(path):
    print(file)     
    img1= cv2.imread(file)
    
    img = cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY)

    regions = grain_segmentation(img)

    grain_number = 1
    for region_props in regions:
        output_file.write(file+",")
        output_file.write(str(grain_number) + ',')
    
 #       output_file.write(str(region_props['Label']))
        for i,prop in enumerate(propList):
            if(prop == 'Area'): 
                to_print = region_props[prop]*pixels_to_um**2   
            elif(prop == 'orientation'): 
                to_print = region_props[prop]*57.2958  
            elif(prop.find('Intensity') < 0):          
                to_print = region_props[prop]*pixels_to_um
            else: 
                to_print = region_props[prop]     
            output_file.write(',' + str(to_print))
        output_file.write('\n')
        grain_number += 1

output_file.close()   