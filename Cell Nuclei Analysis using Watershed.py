# -*- coding: utf-8 -*-
"""
Created on Sun May 17 03:24:29 2020

@author: thejunaidiqbal
"""



"""

This program performs cell counting and size distribution analysis and dumps results into a csv excel file.
It uses watershed segmentationfor better segmentation.
Similar to grain analysis except here we segment cells. 
"""

import cv2
import numpy as np
from matplotlib import pyplot as plt
from scipy import ndimage
from skimage import measure, color, io

img = cv2.imread("images/Osteosarcoma.tif")

cells=img[:,:,0]  


pixels_to_um = 0.454 # 1 pixel = 454 nm 

ret1, thresh = cv2.threshold(cells, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)


#Morphological operations to remove small noise - opening
kernel = np.ones((3,3),np.uint8)
opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 2)

from skimage.segmentation import clear_border
opening = clear_border(opening) #remove edge

sure_bg = cv2.dilate(opening,kernel,iterations=10)


dist_transform = cv2.distanceTransform(opening,cv2.DIST_L2,5)


#print(dist_transform.max()) 
ret2, sure_fg = cv2.threshold(dist_transform,0.5*dist_transform.max(),255,0)

sure_fg = np.uint8(sure_fg)
unknown = cv2.subtract(sure_bg,sure_fg)

ret3, markers = cv2.connectedComponents(sure_fg)


markers = markers+10

markers[unknown==255] = 0
#plt.imshow(markers, cmap='jet')   

markers = cv2.watershed(img,markers)

img[markers == -1] = [0,255,255]  

img2 = color.label2rgb(markers, bg_label=0)

#cv2.imshow('Overlay on original image', img)
#cv2.imshow('Colored Grains', img2)
#cv2.waitKey(0)


regions = measure.regionprops(markers, intensity_image=cells)

for prop in regions:
    print('Label: {} Area: {}'.format(prop.label, prop.area))



propList = ['Area',
            'equivalent_diameter', 
            'orientation', 
            'MajorAxisLength',
            'MinorAxisLength',
            'Perimeter',
            'MinIntensity',
            'MeanIntensity',
            'MaxIntensity']    
    

output_file = open('cell_measurements.csv', 'w')
output_file.write(',' + ",".join(propList) + '\n') 

for region_props in regions:
    output_file.write(str(region_props['Label']))
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
