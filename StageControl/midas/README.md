

# Sections 
## Frontend 

Defines the frontend equipment stuff. All of the midas code

## Pages

html code for the pages we see on the midas page 

## Utilities 

Utility code used by the frontend code. 
These scripts are all super independent and generally are just used to communicate with the equipment 

## Equipment Notes

### Buffer Names

### Equipment IDs

- LEDMidas: 16
- PicoScope: 10 
- PumpConnection: 11 
- ELLxStage: 12


# Automation

## Frontends 

### fePico - data taking and DAQ automation

Watches
    - leds enabled
    - stage location
    - led adc

Script will adjust *settings* for the stage and the board 


Stages/LED frontends will see that those have changed
Teh