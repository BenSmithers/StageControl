# Serial Control of ELLx linear stage 

This is still a work in progress! 

# Usage 

Initialize a connection by creating a `ELLxConnection` object and passing the full path to the usb interface in `/dev`. 
On linux, you may have to first allow such a connection using 
```
sudo chmod 666 /path/to/interface
```
Then, you can control the linear stage by using the various member functions of the `ELLxConnection` class. 

A value of `pulses_per_dev` can be provided to convert between stage-pulses and some physical quantity (degrees, mm, etc). 
A default of 1024 is currently in-place. 

# Todo
    - code should be using asynch/thread mechanisms. Current implementation means the code will lock up if no reply is received. Ideally, there should be a repsponse management thread and a message-send thread/queue. 