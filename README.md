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

2. Then there are additional setpoints you can configure to change the bevaviour
    - "Program": a selector in which you can choose wich porgram to run: Off (no programming, only manual), Day (Boiler temperature is based on heating cuver and reference room compensation), Night (Boiler is switched off, unless below night setpoint), Frost Protection (Boiler is switched off, unless temperature below fp setpoint)
    - "Temperature compensation": setting the parameters will make sure that if reference room temperature is below the "setpoint", the boiler temperature is raised with the difference in temperature, multiplied by the "Temperature compensation" setting. E.g. when you want it bo be 20 Celcius, but actual temp is 18 celcius en temperature compensation is set to 5 degrees Celcius, the boiler temperature will be raised with 10 degreees celcius
    - "Day Setpoint", "Night Setpoint", "Frost Protection Setpoint". The setpoint values to aim for in the different pograms
    - "Minimum Boiler Temperature" and "Maximum Boiler Temperature": No matter what the outcome of the calculations above. The boiler temperature will never exceed these values.

3. And then there some devices to let you control the boiler
    - "Boiler Setpoint". When the program is Off, you can use this setpoint to manually set the boiler termpature
    - "DHW Setpoint". If you have a SWH system, you can use this setpoint to manually set the water temperature
    - "EnableCentralHeating". When the program is Off, you can use this switch to manually switch on or off the central heating
    - "EnableCooling", if your system supports: You can use this switch to manually switch on or off cooling
    - "EnableHotWater", if your system supports: You can use this switch to manually switch on or off the hotwater system

4. And then there is information reported about the boiler: 
    - "Central Heating": the reporting of opentherm if central heating is switched on
    - "Cooling": the reporting of opentherm if cooling is switched on
    - "HotWater": The reporting of opentherm if hotwater is switched on
    - "Flame": is the Flame on or Off
    - "Pressure": The pressure in the boiler
    - "Modulation": The modulationlevel of the boiler
    - "BoilerTemperature": The temperature of the boiler
    - "ReturnTemperature": The temperature of the water returning to the boiler
    - "DHWTemperature": The temperature of the hot water supply

5. All things work as regular domoticz devices, so you can add devices to your interface to make them visible in the GUI and you can use timers to program the central heating to switch on or of when you like, or change the setpoints at desired moments.

Have fun!

## Contributions
Last but not least: I built this plugin for according to my own wishes. But if you like to add things, feel free to program them yourself, just as long as you make PR's, so other users can benefit from your enhancements to

## Testing
At the moment of writing my opentherm interface was not yet deliverd, so everything is tested, but stubbed and i am still waiting to test again a real boiler ;-)

