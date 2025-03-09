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

## Normal Data Taking 

Data taking is all done throught the `Control` tab.

### One-LED Runs

1. Choose an LED frequency from the drop-down menu at the top. Press "Go!"beside the drop down menu.
2. Select an appropriate ADC to get ~0.3 counts per pulse. Try just getting one from this table 

| nm  | ADC |
|-----|-----|
| 450 | 720 |
| 410 | 756 |
| 365 | 617 |
| 295 | 589 |
| 278 | 773 |

3. Select the MHz flash rate from the "Flash Rate" drop-down menu.
4. Choose which water type is present in the water drop down menu, beside the "Update Filename" button.
5. Make sure "Rotate Wavelengths?" is unchecked. 
6. If auto-refill is needed, consult the [[#Auto-Refilling]] section, below
7. Press the "Start Run" button
8. Controls will lock out until the "Stop Run" button is pressed.  

### Multi-LED Runs 
1. Ensure the LED is turned on and at the MHz frequency. Press "Go!" beside the wavelength check button, press the "Set ADC" button, and then ensure the "Flash Rate" drop-down menu is set to the MHz frequency. 
2. Check the "Rotate Wavelengths" checkbox. 
3. If auto-refill is needed, consult the [[#Auto-Refilling]] section, below
4. Press the "Start Run" button
5. Controls will lock out until the "Stop Run" button is pressed

### Auto-Refilling 

Auto-refill automatically refills the tube on a timer. Only a few water types are supported right now. 

1. Choose an appropriate refill period (this will be communicated ahead of time). 120 minutes is a good one 
2. Choose which kind of water to refill *with.* Only supply water and return water are supported right now. 

## Filling or Draining the water chamber
Navigate to the `Pump Operations` tab, when there you should see a picture of the water filtration layout. 
In general, you should *only* need to use the automated buttons at most! 
Do not manually turn valves or pumps on unless you know what you are doing. 
The buttons:

 - Drain Chamber: drains the chamber
 - Fill with Supply Water: drains the chamber, then fills with water from the supply line
 - Fill with Return Water: drains the chamber, then fills with water from the return line. Also known as tank water
 - Fill with Osmosis: drains the chamber, then fills with reverse osmosis water. This takes about 45 minutes. You may see it periodically pressurizing the RO pressure vessel, waiting as the RO tank fills, and then waiting as the RO tank fills the chamber. It'll swap between these frequently. 

# What to do when... 

## Air keeps getting pumped into the return line. 

This happens when there is no water in the open tank (the white plastic drum), but the return pump keeps running (a relatively quiet pump). 
If this keeps happening, turn the WMS cabinet off (you will see the green lights turn off), and contact the experts (Ben Smithers - bsmithers@triumf.ca - CERN Phone 69399).

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

