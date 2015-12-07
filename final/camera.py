from PIL import Image, ImageFilter
import picamera
from PIL import ImageChops
import math, operator
import time
camera = picamera.PiCamera()

#put all in a while loop, always wait for a signal to take another photo and process again

camera.capture('dump.jpg')
time.sleep(3)
camera.capture('orig.jpg') #"empty room"
time.sleep(3)
camera.capture('update.jpg') #capture new image whenever there is a change

def rmsdiff(im1, im2):
    	diff = ImageChops.difference(im1, im2)
    	h = diff.histogram()
    	sq = (value*(idx**2) for idx, value in enumerate(h))
    	sum_of_squares = sum(sq)
    	rms = math.sqrt(sum_of_squares/float(im1.size[0] * im1.size[1]))
    	return rms
img1 = Image.open('orig.jpg')
img2 = Image.open('update.jpg')
img1 = img1.filter(ImageFilter.FIND_EDGES)
img1.save('orig.jpg')
img2 = img2.filter(ImageFilter.FIND_EDGES)
img2.save('update.jpg')

diff = ImageChops.subtract(img2, img1)
diff.save('diff.jpg')

diff = Image.open("diff.jpg").convert('1')
black, white = diff.getcolors()

print black[0] #number of black pixels
print white[0] #number of white pixels

if (white[0] < 3500):
	print "relatively empty"
elif (white[0] <5000):
	print "kind of full"
else:
	print "full"
