Docker currently working but still a work in progress to make it more user friendly. I'll put it on dockerhub when fully functional
Currently working from a lubuntu 16.04 host, (with ps3 controller working),  though there is still some configuration
I took https://github.com/fcwu/docker-ubuntu-vnc-desktop as a starting point 

build using : 
docker build -t linn-photobooth . 

run the image using (set mypassword to the password you want to use and the persistent folder path):
If you need all functionalities (i.e. bluetooth ps3 controller) you will need to give more permissions
docker run --privileged  --cap-add=ALL --net=host --device=/dev/video0:/dev/video0 -v /lib/modules:/lib/modules -v /var/run/dbus:/var/run/dbus -v ABSOLUTE_PATH_TO_HOST_LINN-PHOTOBOOTH_PERSISTENT_FOLDER:/root/Linn-Photobooth/persistent -p5900:5900 -p6080:80 -e VNC_PASSWORD=mypassword linn-photobooth

Otherwise use :
docker run --privileged --net=host --device=/dev/video0:/dev/video0 -v ABSOLUTE_PATH_TO_HOST_LINN-PHOTOBOOTH_PERSISTENT_FOLDER:/root/Linn-Photobooth/persistent -p5900:5900 -p6080:80 -e VNC_PASSWORD=mypassword linn-photobooth

Then connect via vnc :
either vncviewer -fullscreen localhost:5900
or go to http://localhost:8080

Inside the container 

cd /root/Linn-Photobooth

<Optional : For remote art>
Configure remoteart.sh with your art server username and ip
Make sure you can ssh without password inside your artserver using ssh-copy-id
</Optional>
Then
python3 photobooth.py

Check that files are correctly saved inside both host and container

If you use the persistent folder it will use ROOT permissions so when you are finished on host 
you can get your original permissions back with sudo chown -R username persistent


