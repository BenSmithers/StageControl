# Water Monitoring Control Software

To launch the water monitoring interface, navigate to the home folder in a terminal. 
If there is no terminal open, press `Ctrl+Alt+T` to launch one. 
Then, execute the `launch.sh` bash script. 
This will start the water quality monitoring GUI. 

## Changing to a different LED 

Once the GUI has been launched, navigate to the `Control` tab. 
On the top-left, there is a drop-down menu for selecting a desired LED; select the desired wavelength and then hit "Go!" beside the drop-down menu. 
In the log in the center of the window, you should see a a series of messages something like 
```
[timestamp] : LED -- L1 
[timestamp] : 0ma00002800
[timestamp] : 0PO00002800
```
The first represents a change in the active LED. 
The second message is the encoded command sent to the thorlabs linear stage.
The third is the response from the board. 

## Filling or Draining the water chamber
Navigate to the `Pump Operations` tab. 
You should see a picture of the water filtration apparatus. 


### Drain The Chamber
To drain the chamber, press the `Drain Chamber` button. 
This will lock out the controls and turn Pump 2 on until there is consistently no flow coming through Flowmeter 4. 
To disable the lock-out and manually take over, press `Stop Automation.` 

### Filling with Osmosis Water
Press the `Fill with Osmosis` button. 
As before, this will temporarily lock out the controls. 
Then it will drain the chamber as described above. 
Finally, it will turn on SV1, SV2, PU1, and BV5. 
After 2.5 seconds, BV6 will be engaged. 
Once flow is consistently seen through Flowmeter 3, the pumps will be disengaged and all valves returned to their off-positions. 

### Filling with Filtered Water 
This procedes identically to the osmosis water, although BV5 is not turned on while BV2 and BV4 are turned on. 

# What to do when... 

## You get a high-pressure warning
The system should automatically turn SV1, SV2, and PU1 off.
If it does not, make sure those boxes do not have a check-mark. 
This should shut off the high-pressure water supply to the system.

Then, contact [Add name and contact later so it's not on github].

## You get a high-temperature warning. 

This is likely the UV sterilizer. Turn this off, then contact [Add name and contact later so it's not on github]. 

## You get a [...] not found error

Odds are permissions are set up wrong for the LED board or for the linear stage. 

### Verify the paths
Check the paths listed in the `constants.py` script in the full file path
```
    /home/watermon/software/StageControl/StageControl/gui
```
Ensure that the `LED_BOARD_USB` and `STAGE_USB` entries point to real file paths. 
You can check by running 
```
    ls -lh /path/listed/in/file
```
If those do not exist, but something similarly named does, you could try using the similarly named entries.
If there are no such entries, contact an expert. 
If they _do_ exist, check the permissions (see below). 

### Set the permissions 

For each of those paths, try running 
```
    sudo chmod 666 /path/listed/in/file
```
You will need the password used to log in to this machine. 

If errors persist, contact an expert.



# Todo
    - code should be using asynch/thread mechanisms. Current implementation means the code will lock up if no reply is received. Ideally, there should be a repsponse management thread and a message-send thread/queue. 