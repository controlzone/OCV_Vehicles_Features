import cv2
from keypoint_data import KeypointData
import time

st = time.time()
print "Loading seed car"
img = cv2.imread('car.png')
img_mask = cv2.imread('car_mask.png', 0)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

print "Showing images"
cv2.imshow("Img", img)
cv2.imshow("Mask", img_mask)
cv2.imshow("Gray", gray)
cv2.moveWindow("Img", 0, 35)
cv2.moveWindow("Mask", 150, 35)
cv2.moveWindow("Gray", 300, 35)
cv2.imshow("Img", img)
cv2.imshow("Mask", img_mask)
cv2.imshow("Gray", gray)
#cv2.waitKey(300)

print "Creating SIFT"
##sift = cv2.SIFT(nfeatures=0, nOctaveLayers=5, contrastThreshold=0.05
##                , edgeThreshold=30, sigma=1.5)     # opencv 2.4
sift = cv2.xfeatures2d.SIFT_create(nfeatures=0, nOctaveLayers=5
                                   , contrastThreshold=0.05, edgeThreshold=30
                                   , sigma=1.5)   # opencv 3.0.0
print "Extracting keypoints and descriptors"
kp, des = sift.detectAndCompute(gray,img_mask)
print "Drawing keypoints"
cv2.drawKeypoints(img, kp, img)
##img = cv2.drawKeypoints(img, keypoints = kp)   # 2.4.9
print "Writing image"
cv2.imwrite('sift_keypoints.png', img)

cv2.imshow('SIFT', img)
cv2.moveWindow('SIFT', 450, 35)
cv2.waitKey(500)
print "Creating pickle"
k = KeypointData(kp, des)
print "Saving file"
k.save("keypoints.p")
print "Done"
end = time.time()
dif = end - st
print dif
