import cognitive_face as CF
import json
import numpy as np
import cv2

KEY = '0118754ef3d3423a91a28c21fab6e342'  # Replace with a valid Subscription Key here.
CF.Key.set(KEY)

BASE_URL = 'https://westus.api.cognitive.microsoft.com/face/v1.0/'  # Replace with your regional Base URL
CF.BaseUrl.set(BASE_URL)

img_url = 'https://raw.githubusercontent.com/Microsoft/Cognitive-Face-Windows/master/Data/detection1.jpg'
img_url = r'C:\Users\Florin\Pictures\Camera Roll\me.jpg'
result = CF.face.detect(img_url)
print(result)

print(result[0]['faceRectangle'])


#obtain face rectangle
faceRectangle = result[0]['faceRectangle']
top = faceRectangle['top']
left = faceRectangle['left']
width = faceRectangle['width']
height = faceRectangle['height']

img = cv2.imread(img_url)
cv2.rectangle( img, ( left, top ), ( left + width, top + height ), ( 100, 255, 100 ), 2 )
cv2.imshow('python', img)
cv2.waitKey(0)
cv2.destroyAllWindows()

