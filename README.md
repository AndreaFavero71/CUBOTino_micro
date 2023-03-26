# CUBOTino micro

This repo contains the relevant files to make CUBOTino micro: World's smallest Rubik's cube solver robot. <br />
![title image](/images/title.jpg)

More info are available at: https://www.instructables.com/CUBOTtino-Micro-the-Worlds-Smallest-Rubiks-Cube-So/

An impression of the robot: https://youtu.be/EbOHhvg2tJE



# How to use it:
1. Flash your SD card according to the procedure in the [document here](doc/How_to_make_CUBOTino_micro_20230326.pdf) , Chapter 12, Step1 and Step2.
2. Put the sd card in the pi and power it. You can monitor the boot process if you connect an hdmi monitor to it but it is not essential. 
3. Try to connect to the Raspberry Pi via SSH. On Windows you can use Putty. On linux and mac you can type directly:
```
ssh pi@cubotino.local
```
4. If you can't reach the pi like this, you will have to scan your network to find the IP to use
5. After you are connected via ssh, type the following commands in the shell:
```
git clone https://github.com/AndreaFavero71/CUBOTino_micro.git
cd cubotino_micro/src
sudo ./install/setup.sh
```
6. Make sure the script runs without error until the end. It should ask you to reboot. Type 'y' and hit enter. You should get the proper environment after reboot at that point
7. If there is any error during the script execution try to fix it and rerun the script again


# Build the robot:
Follow the instructions (saved at /doc folder)


# Tuning the servos position via GUI (via VNC):
```
cd ~/cubotino_micro/src
source .virtualenvs/bin/activate
python Cubotino_m_servos_GUI.py
```
![title image](/images/Servo_tuning_GUI_01.PNG)


# Starting the solver manually
From a shell, you can run the main python script like this:
```
cd ~/cubotino_micro/src
source .virtualenvs/bin/activate
python Cubotino_m.py
```
of course, you can replace `Cubotino_m.py` by any other python scripts as mentioned in the documentation.
There also are some arguments that can be passed.



# Enabling autostart
When everything is tuned and you want to autostart the software automatically on reboot, just type :
```
    sudo crontab -e
```
select the nano editor '1' then go to the last line of the window and remove the first '#' character of the line . This uncomment the startup script that launches cubotino on startup. You can reboot after to test it.

# VNC connection
You can always connect with ssh. If you prefere VNC you can download the RealVNC client (this is the one I use). You just have that start it like this:
```
vncviewer cubotino.local
```
It will ask for the credential. Use 'pi' and the same password you use for ssh. You should have a desktop version in this way

Check out the "How_to_make ...  .pdf" document (at /doc folder) for further info.<br /><br />


# Please leave a feedback if you build it
I hope many of you will decide to build your own CUBOTino micro, and that you'll enjoy it as much much as I did. <br />
I hope you will also post an "I Made it", on the Instructables site of this project (link above); <br />
I can ensure you, seeing a new born CUBOTino makes me feel very well 🙂

