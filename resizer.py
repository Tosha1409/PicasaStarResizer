#!/usr/bin/python
import re, os, os.path, sys
from PIL import Image

#directories for input and output
inputdir = ""
outputdir = ""
#JPEG picture quality/compression settings
picturequality=80

#Procedure that checking out if path for file exits, if it doesnt, then it creates nessesary directories
def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

#Procedure for checking what files in current directory marked with "star"
def find_with_star(fpath):
	#possible file formats
	alist_filter = ['.jpg', '.jpe', 'jpeg', '.Jpg', '.Jpe', 'Jpeg', '.JPG', '.JPE', 'JPEG']
	#initializing empty file list
	filelist = []
	#opening picasa.ini file if possible, if not programm writes at what directory file was missed
	try:
		f = open(fpath+".picasa.ini", "rb")
	except IOError:
		print 'not possible to open or missed file picasa.ini at', fpath
	else:
		#reading every line of picasa ini file
		for line in f:
			#removing unnesary whitespaces
			line.strip()
			line=' '.join(line.split())
			#checking last last 5 symbols of line to find out is it begining of file descibtion or not, 
			#and putting filename to variable file m
			if line[-5:-1] in alist_filter: 
				line=line.replace('[','')
				line=line.replace(']','')
				filem=line;
			if line == 'star=yes':
			#checking if there is line that marks star, if yes then putting file to list of marked files
				filelist.append(filem)
		f.close
	#return list of marked files
	return (filelist)
			
#Procedure for resizing images
def resize(img, box, fit, out):
    '''Downsample the image.
    @param img: Image -  an Image-object
    @param box: tuple(x, y) - the bounding box of the result image
    @param fix: boolean - crop the image to fill the box
    @param out: file-like-object - save the image into the output stream
    '''
    #checking if image vertical or horizontal and chaging settings if it required
    if img.size[0]<img.size[1]:
	box = [box[1], box[0]]
	
    #preresize image with factor 2, 4, 8 and fast algorithm
    factor = 1
    err = 0
    while img.size[0]/factor > 2*box[0] and img.size[1]*2/factor > 2*box[1]:
        factor *=2
    if factor > 1:
        img.thumbnail((img.size[0]/factor, img.size[1]/factor), Image.NEAREST)
 
    #calculate the cropping box and get the cropped part
    if fit:
        x1 = y1 = 0
        x2, y2 = img.size
        wRatio = 1.0 * x2/box[0]
        hRatio = 1.0 * y2/box[1]
        if hRatio > wRatio:
            y1 = int(y2/2-box[1]*wRatio/2)
            y2 = int(y2/2+box[1]*wRatio/2)
        else:
            x1 = int(x2/2-box[0]*hRatio/2)
            x2 = int(x2/2+box[0]*hRatio/2)
	try:
        	img = img.crop((x1,y1,x2,y2))
 	except IOError:
		print 'file is corrupted(crop)'
		err=1
    if err == 0:
    	#Resize the image with best quality algorithm ANTI-ALIAS
    	try:    
    		img.thumbnail(box, Image.ANTIALIAS)
    	except IOError:
		print 'file is corrupted(resizing)'

    	#save it into a file-like object
    	try:
    		img.save(out, "JPEG", quality=picturequality)
    	except IOError:
		print 'problems with saving file'

#Procedure that resizing all files in current directory and moves them to correct place
def resizing(cur_dir, sizes):
	#printing current directory
	print cur_dir 
	#getting list of file marked with star in current directory
	files = find_with_star (cur_dir)
	#creating same subdirectory in output directory
	ensure_dir (outputdir+cur_dir[len(inputdir):].strip())
	for filename in files:
		#resizing file
		print outputdir+cur_dir[len(inputdir):]+filename
		try:
			i = Image.open(cur_dir+filename)
		except IOError:
			print 'doesnt exits', filename
		else:
			resize(i, sizes, 1, outputdir+cur_dir[len(inputdir):]+filename)
			################################
			# copy EXIF data
    			source_image = pyexiv2.Image(cur_dir+filename)
    			source_image.readMetadata()
    			dest_image = pyexiv2.Image(outputdir+cur_dir[len(inputdir):]+filename)
    			dest_image.readMetadata()
    			source_image.copyMetadataTo(dest_image)
    			# set EXIF image size info to resized size
    			dest_image["Exif.Photo.PixelXDimension"] = image.size[0]
    			dest_image["Exif.Photo.PixelYDimension"] = image.size[1]
    			dest_image.writeMetadata()
    			################################

if len(sys.argv) != 6:  
	sys.exit("Command line syntax: [path 1] [results path] [x] [y] [compressopm]")

inputdir = sys.argv[1]
outputdir = sys.argv[2]
if inputdir[-1:] != "/": inputdir +="/"
if outputdir[-1:] != "/": outputdir +="/"

#taking and fixin resolution values if them was put in wrong order
if int(sys.argv[3]) > int(sys.argv[4]):
	sizes = (int(sys.argv[3]), int(sys.argv[4]))
else:
	sizes = (int(sys.argv[4]), int(sys.argv[3]))

if int(sys.argv[5]) <= 100:
	picturequality = int(sys.argv[5]) 
	
print "Resizing to "+sys.argv[3]+"X"+sys.argv[4]+"..."

#Making folder for final files if it doesnt exits
if not os.path.exists(outputdir):
	os.makedirs(outputdir)

#first run for root directory
resizing (inputdir, sizes)

#walking directory script for resizing of all other directories expect root ones
for dirname, dirnames, filenames in os.walk(inputdir):
    for subdirname in dirnames:
	current_dir=os.path.join(dirname, subdirname)+"/"
	resizing (current_dir, sizes)