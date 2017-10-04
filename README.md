"# DayEye" 

Links:
https://jireren.github.io/blog/2016/02/27/face-recognition-system-based-on-raspberry-pi-2/



## Install:
sudo apt-get install python-pip
sudo apt-get install python-dev
sudo apt-get install mosquitto-clients

## Python depencies
sudo pip install picamera
sudo pip install paho-mqtt
sudo pip install ruamel.yaml

## Run
before running module, execute the following
"source setup_pythonpath"


## Text to speach
https://elinux.org/RPi_Text_to_Speech_(Speech_Synthesis)

sudo apt-get install mplayer

sudo apt-get install festival
sudo echo "Macadamian Hackatlon 2017" | festival --tts

espeak -ven+f3 -k5 -s150 "I've just picked up a fault in the AE35 unit"
espeak -ven+f3 -k5 -s150 "Macadamian Hackatlon 2017"
sudo apt-get install espeak python-espeak

./say.sh "Macadamian Hackatlon 2017"

sudo apt-get install libttspico-utils
pico2wave -w lookdave.wav "Macadamian Hackatlon 2017" && aplay lookdave.wav

## Speach to text
https://github.com/StevenHickson/PiAUISuite

git clone https://github.com/StevenHickson/PiAUISuite.git
cd PiAUISuite/Install
./InstallAUISuite.sh
ln -s /usr/lib/arm-linux-gnueabihf/libboost_regex.so.1.55.0 /usr/lib/arm-linux-gnueabihf/libboost_regex.so.1.49.0
