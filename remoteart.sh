#!/bin/bash
#./remoteart.sh localfileimage stylename outname
filename="photos/$1" ;
echo $filename ;
#scp "${filename}" beast:~/fast-neural-style/photos ;
rsync -a -v --ignore-existing "${filename}" beast:~/fast-neural-style/photos ;
ssh beast \
"cd ~/fast-neural-style; \
bash -i th fast_neural_style.lua \
  -model "stylemodel/$2.t7" \
  -input_image "${filename}"  \
  -output_image "output/$3" \
  -image_size 1920 \
  -gpu $4" 

#scp beast:"~/fast-neural-style/output/$3" "art/$3"
rsync -a -v --ignore-existing beast:"~/fast-neural-style/output/$3" "art/$3"