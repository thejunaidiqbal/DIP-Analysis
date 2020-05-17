# -*- coding: utf-8 -*-
"""
Created on Sun May 17 03:12:13 2020

@author: thejunaidiqbal
"""


"""
This program performs grain size distribution analysis and dumps results into a csv (Excel) file.

Step 1: Read image and define pixel size
Step 2: Denoising, if required and threshold image to separate grains from boundaries.
Step 3: Clean up image, if needed and create a mask for grains
Step 4: Label grains in the masked image
Step 5: Measure the properties of each grain 
Step 6: Output results into a csv file
"""

import cv2
import numpy as np
from matplotlib import pyplot as plt
from scipy import ndimage
from skimage import measure, color, io

img = cv2.imread("images/grains.jpg", 0)

pixels_to_um = 0.5 #bcuz 1 pixl = to 500nm

#cropped_img = img[0:450, :]   


#plt.hist(img.flat, bins=100, range=(0,255))

ret, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

kernel = np.ones((3,3),np.uint8) 
eroded = cv2.erode(thresh,kernel,iterations = 1)
dilated = cv2.dilate(eroded,kernel,iterations = 1)

mask = dilated == 255
#print(mask)   

#from skimage.segmentation import clear_border
#mask = clear_border(mask)   

io.imshow(mask)  
#io.imshow(mask[250:280, 250:280])   


s = [[1,1,1],[1,1,1],[1,1,1]]
labeled_mask, num_labels = ndimage.label(mask, structure=s)

img2 = color.label2rgb(labeled_mask, bg_label=0)

cv2.imshow('Colored Grains', img2)
cv2.waitKey(0)


#print(num_labels) 



clusters = measure.regionprops(labeled_mask, img)


#print(clusters[0].perimeter)


    
propList = ['Area',
            'equivalent_diameter', 
            'orientation', 
            'MajorAxisLength',
            'MinorAxisLength',
            'Perimeter',
            'MinIntensity',
            'MeanIntensity',
            'MaxIntensity']    
    

output_file = open('image_measurements.csv', 'w')
output_file.write(',' + ",".join(propList) + '\n')

for cluster_props in clusters:
    output_file.write(str(cluster_props['Label']))
    for i,prop in enumerate(propList):
        if(prop == 'Area'): 
            to_print = cluster_props[prop]*pixels_to_um**2   
        elif(prop == 'orientation'): 
            to_print = cluster_props[prop]*57.2958  
        elif(prop.find('Intensity') < 0):          
            to_print = cluster_props[prop]*pixels_to_um
        else: 
            to_print = cluster_props[prop]
        output_file.write(',' + str(to_print))
    output_file.write('\n')
output_file.close()   
