#!/bin/bash
#./remoteart.sh localfileimage stylename outname
filename="persistent/photos/$1" ;
photopath="photos/$1";
echo $filename ;
echo $photopath
#scp "${filename}" beast:~/fast-neural-style/photos ;
rsync -a -v --ignore-existing "${filename}" beast:~/fast-neural-style/photos ;
ssh beast \
"cd ~/fast-neural-style; \
bash -i th fast_neural_style.lua \
  -model "stylemodel/$2.t7" \
  -input_image "${photopath}"  \
  -output_image "output/$3" \
  -image_size 1920 \
  -gpu $4" 

#scp beast:"~/fast-neural-style/output/$3" "art/$3"
rsync -a -v --ignore-existing beast:"~/fast-neural-style/output/$3" "persistent/art/$3"