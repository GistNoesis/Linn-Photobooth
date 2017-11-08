I have trained a few styles. 
For remoteArt.sh to work :
You need to replace "beast" by username@ipofyourlocalartserver and configure it so you can ssh into it without having to input the password.
You can use ssh-copy-id for this. Even on localhost we go over ssh.
The fast neural style is intended to be cloned from https://github.com/jcjohnson/fast-neural-style into ~
Then you create a folder named photos, and a folder named stylemodel inside the fast-neural-style folder
You can also use the provided script to train multiple styles
