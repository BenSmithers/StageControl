# Water Monitoring Control Software

To launch the water monitoring interface, navigate to the home folder in a terminal. 
If there is no terminal open, press `Ctrl+Alt+T` to launch one. 
Then, execute the `launch.sh` bash script. 
This will start the water quality monitoring GUI. 

## Starting Your Shift

On the `control` tab, verify that the emails are correct for the two people currently on shift. 
You may need to manually press "update emails" if the line editor did not automatically update. 
If an address is not accurate, edit it. 

Once you've verified the addresses are accurate, click "Test Alert Email" and you should receive a test email from the wcte alert bot shortly. 
If you don't receive an email, be sure to check your spam folder.

If you want to opt-out of receiving the emails, just replace the auto-populated entry of your address with a blank line. 
You will _only_ receive an email when there is a serious issue which may require prompt action; this is not necessarily recommended. 

## First time setup 

You will need a monitor and a keyboard for first-time setup. A keyboard is optional. 
Once the setup is complete, these are not longer required. 

### Network Setup 

Plug the ethernet cable in to the computer, turn the computer on, and sign in. 
If we have been provided with a network address, you can go to the Static IP section below. 
Otherwise, go to the dynamic IP section beneath that. 

#### Static IP 

On the top right corner, click the arrow pointing down and select settings. 
Under "network" click the gear under the "wired" connection category. 
Choose "manual" under IPv4, then enter in the IP Address, the netmask, and the gateway. If a DNS is provided, enter that in too. If not, you can use `8.8.8.8` or `8.8.4.4`; these are popular google-managed DNS servers. 

You should now be able to access the internet on the computer. 
If a domain name (like, `watermon.cern.ch`) was provided, you should be able to SSH to that address. 

#### Dynamic IP 

If _no_ static IP address was provided, then instead we'll have to use a dynamic address. 
On the top right corner, click the arrow pointing down and select settings. 
Under "network" click the gear under the "wired" connection category, then click "Automatic" under IPv4 method. 
Press apply.  
Wait a moment as the connection establishes. 
You will then need to open a web browser (the computer already has firefox), and should try to go to a CERN webpage and proceed with the normal CERN device registration. 

Afterwards, run `ifconfig` in a terminal. You will see an output like 
```
enp1s0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 10.1.3.129   netmask 255.255.224.0  broadcast *************
        inet6 ************  prefixlen 64  scopeid 0x20<link>
        ether ************  txqueuelen 1000  (Ethernet)
        RX packets 13888376  bytes 1383517057 (1.3 GB)
        RX errors 0  dropped 108953  overruns 0  frame 0
        TX packets 199207  bytes 249137742 (249.1 MB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

The number beside `inet` is the machine's IPv4 address. You can now SSH directly to the machine like so
For instance:
```
    ssh watermon@10.1.3.129 
```
### Setting up the LED board and the Stage 

Before plugging in anything, run
```
ls /dev/ | grep USB
```
and note what shows up. It might be nothing.
Plug in the LED board, and run the command again.
You will likely see something has appeared now, highlight the filepath it shows and copy it (Ctrl+Shift+C).
Open the path list at 
```
/home/watermon/software/StageControl/StageControl/gui/constants.py 
```
and replace the path definition for `LED_BOARD_USB` with the path you just copied. 
Save this file, then plug in the thorlabs stage. 
Run the same `ls` command, and note that a second path has appeared. Copy the new one, and add it to the `STAGE_USB` variable in the same file as before

Now, run 
```
    sudo chmod 666 /dev/tty.USB0
    sudo chmod 666 /dev/tty.USB1
```
where you will replace each path with the ones from before. 
The password will be the same as the one you logged in with. 

Now if you launch the gui,
```
   /home/watermon/launch.sh
```
it should start up successfully. 
You should also now be able to control the LED board and the stage through the GUI.
Test it out, try selecting different wavelengths and make sure it actually lights up and moves. 

#### Setting up the Pumps and stuff

This still needs some work, will add this soon.

### Starting data-taking

Once the PMTs are powered on and the LED is turned on, try running the PicoScope 7 software and make sure you can see signal in the PMTs.
Be sure the amplifier is also powered on!! 
Go to the `~/software/PicoCode/` folder and try running `python3 measure.py`. 
The Picoscope should click on and you should see an output as it takes data. 
Then, you can edit the cron, 
```
crontab -e
```
and uncomment the last two lines. 
Wait a few minutes; once the time reaches a minute divisible by three, you should hear the picoscope click. 
That means it's taking data now. Good! 

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

This is likely the UV sterilizer. Power the UV sterilizer down and then contact [Add name and contact later so it's not on github]. 
Note: you will probably have to physically flip a switch or unplug a cable. You can not power up or power down the UV sterilizer through the GUI.

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