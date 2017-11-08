 #!/bin/bash
 # folder gpuindex
for i in $( ls $1); do
	filename=$(basename "$i")
	extension="${filename##*.}"
	filename="${filename%.*}"
	echo item: $filename

	th train.lua \
  -h5_file ~/Downloads/coco.h5 \
  -style_image $1/$i \
  -style_image_size 784 \
  -content_weights 1.0 \
  -style_weights 5.0 \
  -checkpoint_name stylemodel/$filename \
  -gpu $2
	
	mv folder/$1 styles
done