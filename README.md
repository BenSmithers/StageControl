# Water Monitoring Control Software

To launch the water monitoring interface, navigate to the home folder in a terminal. 
If there is no terminal open, press `Ctrl+Alt+T` to launch one. 
Then, execute the `launch.sh` bash script. 
This will start the water quality monitoring GUI. 

1. [Starting Data Taking](#starting-data-taking)

    a. [Continuous Flow Monitoring](#continuous-flow-monitoring)

    b. [Regular Refill Monitoring](#regular-refill-monitoring)

    c. [No Flow Refill Monitoring](#no-flow-monitoring)

2. [Shift Checks](#shift-checks)

2. [Interventions](#Interventions)

    a. [Water Leak Found](#water-leak-found)

    b. [Fractional Deviation Exceeds Bounds](#fractional-deviation-exceeds-bounds)
    
    c. [Other Interventions](#other-interventions)

    d. [Bleeding Osmosis Pressure](#bleeding-osmosis-pressure)



# Starting Data Taking

For each of these, an important first step is to ensure the LED flasher board is on and flashing. 

1. Launch the gui using `python launch.py` and wait a few seconds for everything to start up. Make sure you are on the “Control” tab, and you should see a few messages relating to picoscope initialization, usb initialization, and a message saying “starting wms_main”.
2. Choose the 410nm LED, press the "Go!" button beside it.
3. Press the "Set ADC" button; the value is not important. 
4. From the Flash Rate drop-down menu, choose "8MHz".
5. Click "Rotate Wavelengths?" and ensure a checkmark appears beside it.

![led on](readme_images/ledon.png "LEDs On")

6. Press "Start Run". Note the present run number.
    -  You can optionally lower the run number by one _before starting_ to append the data to the previous run. 
7. Go to the “Pump Operations” tab, and press “Start Flow”. You should see Flow 1 and 2 fill up after a moment. If the test chamber was already full, Flow 3 should also fill up.
8. After a few minutes, there should now be a new data file for the new run.
9. Go to the “Plots” tab. Click on the line with a full filepath already present, and select the filename with the run number you saw in step 6.



## Filling or Draining the water chamber
Navigate to the `Pump Operations` tab, when there you should see a picture of the water filtration layout. 
In general, you should *only* need to use the automated buttons at most! 
Do not manually turn valves or pumps on unless you know what you are doing. 
The buttons:

 - Drain Chamber: drains the chamber
 - Fill with Supply Water: drains the chamber, then fills with water from the supply line
 - Fill with Return Water: drains the chamber, then fills with water from the return line. Also known as tank water
 - Fill with Osmosis: drains the chamber, then fills with reverse osmosis water. This takes about 45 minutes. You may see it periodically pressurizing the RO pressure vessel, waiting as the RO tank fills, and then waiting as the RO tank fills the chamber. It'll swap between these frequently. 


# Shift Checks

## Pure Water or Gd

- Is the WMS Remote Desktop window open? If not, please open it on any of the machines with a remote desktop app (the water pc, for instance)
    - Connectio ninformation is on the whiteboard! 
- Is the WMS plot updating? If the data are more than about fifteen minutes old then
    - Check the "Control" tab. Are the data-taking messages there up to date? - If they are not, please notify me on slack (@bsmithers) and post in the shift channel.
- Are the pressures under the "Pump Operations" tab updating every ~5 seconds? 
    - If not you should try to close the WMS Control System, open the terminal window, and re-launch `python launch.py`. Then post in the #water channel and @bsmithers. See [Starting Data Taking](#starting-data-taking) for the starting procedure. 
- Write how long ago the last “Pump Off” event happened. These are shown as vertical gray lines; you may need to scroll a few hours back in time on the plot. These typically happen every 2-4 hours.
    - Following a “Pump Off” event, the monitoring data will be unreliable for approximately 20 minutes. This is expected behavior!
    - The stamps are read as "$day $hour:$minute"
- If the last “pump off” event was more than five hours ago – check the water level in the WMS open tank using the reolink camera.
    - Check the water level in the WMS open tank using the reolink camera. It is visible as a slightly darker portion of the open tank (see the second image), and may be quite hard to see (consider raising the camera resolution).
    - The water level should be between the lower two of the wires entering the side of WMS. If it is well above level sensor 2 (see first image) – this is a major problem. See [Urgent Problems](#urgent-problems) below. The water level may appear close to or just above level sensor 2 - this is typical.
    - Check the “Flow” indicators on the “Pump Operations” page. If flow 1 is 0% but “Pump 1” is checked, this is an indication that either the WMS input pump has died or that the WCTE flow has been interrupted. See [Urgent Problems](#urgent-problems) below
- Check the plot on the "Plots" tab. Are any trends below the 3% mark (lower red dashed line)?
    - If this happens within 20 minutes of a “Pump Off”, this expected behavior. Not a problem.
    - If this happens more than 20-30 minutes after a “Pump Off”, this may indicate a problem! Post screenshots of the plot and the "Pump Operations" tab in the shift channel and @bsmithers. If this is during Gd loading, it may indicate a more serious Gd-related problem and you should tell those involved with the loading.

![Water Levels](readme_images/open_tank_annot.png "Open Tank Annotated")
![Filling Open Tank](readme_images/filling_open_tank.png "Filling Open Tank")


## Gd-Specific

### During the ixing
- Checks of the plot should be done much more frequently; ideally every ~15-20 minutes in the hours following the addition of the Gd.
- It would be best if Gd is only be added if the last "pump off" event was within the last two hours. We do not want to risk the "pump off" happening automatically just after the addition of G; we could loose monitoring for ~20 minutes during a critical moment.

### Forcing a "Pump off" moment

1. Press “Stop Automation”
2. Manually enable “Pump 3”: the box can be checked (and pump enabled) by clicking on it. 
3. Wait approximately 7 minutes. Pump 3 will automatically disable itself when “Water level 1” is no longer checked (meaning the open tank is empty)
4. Press “Start Flow.” You should see pump 1 enable along with a few solenoid valves. 5. After a few seconds flow will be visible in Flowmeters 1, 2, and 3. Flowmeter 5 will show flow a few more seconds later.

 

# Interventions

## Urgent Problems

In the event of a WMS emergency, you should navigate to the “Pump Operations” page and press “Stop Automation”. All flow, except maybe Flow 5, should read 0%. Post in the shift and water channel, @bsmithers (me) on slack, and email me at

Include screenshots of the Pump Operations and  "Plots" page, along with a picture of the open tank.

## Water Leak Found

### If the open tank (barrel) is overflowing 

1. Immediately, under "Control" pres "Stop Run"
2. Ensure all **no** boxes are checked under "Pump Operations." You may need to press "Stop Automation" on this tab, first. 

### If water is leaking near a darkbox

1. Immediately go to the "pump operations" tab and press the button on the top-left "Drain Chamber".
2. Contact an expert (Ben's CERN phone is on the whtieboard)
3. Once it is safe to do so, go to the WMS and clean up the spilled water. You may need to move the desy table left (using the LEFT red button) about 10cm. 
4. Under "Control" press "Stop Run" 
5. Once the chamber is drained, close the valves to WMS 

### Water Leak on the Bench 

1. If the leak is slow, follow the instructions above. 
2. Otherwise, you may just want to shut the valves to WMS to isolate it, and capture as much of the water as possible to minimize the spill. There is a bucket (and maybe a mop) by the water system fence.



## Other Interventions

# What to do when... 

## Air keeps getting pumped into the return line. 

This happens when there is no water in the open tank (the white plastic drum), but the return pump keeps running (a relatively quiet pump). 
If this keeps happening, turn the WMS cabinet off (you will see the green lights turn off), and contact the experts.

## Major Leak is found

If a major leak occurs, like a pipe becoming unseated or worse. 

1. Stop the leak if possible. 
2. Isolate the system. 
3. Fix the leak, if possible. 
4. Contact the experts (see above)

You can probably hold your finger over an unseated tube. 

The system can be isolated by closing the valves in the corner between the WMS cabinet, the WCTE tank, and the wall. 
 

## You get a high-pressure warning
The system should automatically turn SV1, SV2, and PU1 off.
If it does not, make sure those boxes do not have a check-mark. 
This should shut off the high-pressure water supply to the system.

Then, contact [Add name and contact later so it's not on github].

## You get a high-temperature warning. 

This is likely the UV sterilizer. Power the UV sterilizer down and then contact [Add name and contact later so it's not on github]. 
Note: you will probably have to physically flip a switch or unplug a cable. You can not power up or power down the UV sterilizer through the GUI.

## You see mechanical timeout errors

Don't worry about those

## A problem not mentioned here. 	

Often, it's useful to just restart the whole thing.

1. On the `Control` tab, press "Stop Run" if that button is there. 
2. On the `Pump Operations` tab, press "Stop Automation" if that button is click-abble and enabled. 
3. On that tab, if any checkboxes were checked, uncheck them. 
4. Close the window. Press Yes.
5. Restart the gui. In the open terminal re-run `python launch.py` 


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

