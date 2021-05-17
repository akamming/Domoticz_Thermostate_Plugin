# Domoticz_Thermostate_Plugin
Domoticz Plugin for ESP thermostat with weather dependent heating control

## Features
1. Manual control of several boiler features
2. Readout of several boiler sensors as devices in domoticz
3. But mostly: an implementation of a weather dependent heating control thermostat with reference room compensation. 

Weather Dependant Heating Control basically means that the boiler temperature is derived from the outside temperature and very advisable in much automated homes (e.g.  every room has it's own thermostat, so there is no central thermostat to manage best boiler setting) or if you have a fireplace. I will not desribe here what it is and how to use it, this is much better explained on lots of places on the internet like http://tech-controllers.com/blog/heating-curve---what-is-it-and-how-to-set-it

## Prerequisites
1. A wemos D1 with domototicz opentherm handler firmware (https://github.com/akamming/esp_domoticz_opentherm_handler)
2. Connected to an opentherm adatper (like http://ihormelnyk.com/opentherm_adapter)
3. which is connected to an opentherm compatible Boiler
4. A working domoticz installation with at least and make sure you know the IDX numbers of 
    - a working temperature device for measuring the outside temperature
    - a working temperature device for measureing the inside temperature in 1 room (the "reference room")

## installation
1. Install arduino software
2. install additional libraries: 
    - Opentherm library tzapu ihormelyk (for communication with boiler)
    - Wifimanager by tzypu (for user friendly 
3. Install the opentherm handler firmware 
4. Connect the Wemos D1 to the opentherm adapter on pin 2 and 3
5. Connect the opentherm adapter to the boiler 
6. Boot the Wemos D1
7. Connect to Access Point "Thermostat" and follow the instructions to connect the wemos to your wifi connection
8. Log into your router and make sure the Wemos gets a static ip adress
9. install this plugin into domoticz by     
   - cd <your domoticzdir>/plugins
   - git clone https://github.com/akamming/Domoticz_Thermostate_Plugin
   - restart domoticz
   - go to hardware page. The plugin (Weather Dependent Heating Control) should now be visible in the "Type" dropdown
 10. select the plugin, and enter the following as config
    -  the  ip adres of your Wemos
    -  the json command for the external temperature sensor (http://127.0.0.1/json.htm?type=devices&rid=<idx of your temp device>
    -  the json command for the internal  temperature sensor (http://127.0.0.1/json.htm?type=devices&rid=<idx of your temp device>
 11. Click "add"
 12. You are now ready to use the plugin!

## How to use the plugin
1. 1st of all your need to configure your heating curve, by setting the setpoints "Boiler Temp at +20", "Boilertemp at -10" and the "Curvator" selector switch. If you want to know what your curve looks like, taak a look at this example:
![image](https://user-images.githubusercontent.com/30364409/118477419-f010f380-b70e-11eb-9796-9752f7067d76.png)
- Here temperature at +20 is set to 20
- Temperature at -10 is set to 70
- and you can see the effect of the curvature setting.
Basically it states what the boiler temperature setting (y axies) should be for every outside temperature (x axis) 

2. Then there are additional setpoints you can configure
  - "Day Setpoint" and "Temperature compensation": setting the parameters will make sure that if reference room temeperature is below the "day setpoint", the boiler temperature is raised with the difference in temperature, multiplied by the "Temperature compensation" setting. E.g. when you want it bo be 20 Celcius, but actual temp is 18 celcius en temperature compensation is set to 5 degrees Celcius, the boiler temperature will be raised with 10 degreees celcius
  -   
