# USAGE
# python build_logos.py

# import the necessary packages
from config import logos_config as config
from bs4 import BeautifulSoup
import os

# initialize the set of classes we have encountered so far
CLASSES = set()

# create the list of datasets to build
datasets = [
	("train", config.TRAIN_TXT, config.TRAIN_CSV),
	("test", config.TEST_TXT, config.TEST_CSV),
]

# loop over the datasets
for (dType, inputTxt, outputCSV) in datasets:
	# load the contents of the input data split
	print("[INFO] starting '{}' set...".format(dType))
	imageIDs = open(inputTxt).read().strip().split("\n")
	print("[INFO] {} total images in '{}' set".format(
		len(imageIDs), dType))

	# open the output CSV file
	csv = open(outputCSV, "w")

	# loop over the image IDs
	for imageID in imageIDs:
		# build the path to the image path and annotation file
		imagePath = "{}.jpg".format(os.path.sep.join([
			config.IMAGES_PATH, imageID]))
		annotPath = "{}.xml".format(os.path.sep.join([
			config.ANNOT_PATH, imageID]))

		# load the annotation file, build the soup, and initialize
		# the set of coordinates for this particular image
		contents = open(annotPath).read()
		soup = BeautifulSoup(contents, "html.parser")
		coords = set()

		# extract the image dimensions
		w = int(soup.find("width").string)
		h = int(soup.find("height").string)

		# loop over all `object` elements
		for o in soup.find_all("object"):
			# extract the label and bounding box coordinates
			label = o.find("name").string
			xMin = int(o.find("xmin").string)
			yMin = int(o.find("ymin").string)
			xMax = int(o.find("xmax").string)
			yMax = int(o.find("ymax").string)

			# truncate any bounding box coordinates that may fall
			# outside the boundaries of the image
			xMin = max(0, xMin)
			yMin = max(0, yMin)
			xMax = min(w, xMax)
			yMax = min(h, yMax)

			# build a (hashable) tuple from the coordinates
			coord = (xMin, yMin, xMax, yMax)

			# if the coordinates already exist in our `coords` set,
			# ignore the annotation (this is a peculiarity of the
			# logos dataset)
			if coord in coords:
				continue

			# write the image path, bounding box coordinates, and
			# label to the output CSV file
			row = [os.path.abspath(imagePath), str(xMin), str(yMin),
				str(xMax), str(yMax), label]
			csv.write("{}\n".format(",".join(row)))

			# add the bounding box coordinates to our set and update
			# the set of class labels
			coords.add(coord)
			CLASSES.add(label)

	# close the output CSV file
	csv.close()

# write the classes to file
print("[INFO] writing classes...")
csv = open(config.CLASSES_CSV, "w")
rows = [",".join([c, str(i)]) for (i, c) in enumerate(CLASSES)]
csv.write("\n".join(rows))
csv.close()