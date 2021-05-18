# Domoticz_Thermostate_Plugin
Domoticz Plugin for ESP thermostat with weather dependent heating control

## Features
1. Manual control of several boiler features
2. Readout of several boiler sensors as devices in domoticz
3. But mostly: an implementation of a weather dependent heating control thermostat with reference room compensation using any temperature device in domoticz. 
4. All the advantages of a smart thermostate, without the disadvantages of all your personal data in a public cloud

Weather Dependant Heating Control basically means that the boiler temperature is derived from the outside temperature and very advisable in highly automated homes (e.g.  every room has it's own thermostat, so there is no central thermostat to manage best boiler setting) or if you have a fireplace. I will not desribe here what it is and how to use it, this is much better explained on lots of places on the internet like http://tech-controllers.com/blog/heating-curve---what-is-it-and-how-to-set-it

## Prerequisites
1. A wemos D1 with domototicz opentherm handler firmware (https://github.com/akamming/esp_domoticz_opentherm_handler)
2. Connected to an opentherm adatper (like http://ihormelnyk.com/opentherm_adapter)
3. which is connected to an opentherm compatible Boiler
4. A working domoticz installation with at least and make sure you know the IDX numbers of 
    - a working temperature device for measuring the outside temperature
    - a working temperature device for measuring the inside temperature in 1 room (the "reference room")

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
 10. select the plugin, and enter the following config: the  ip adres of your Wemos, the json command for the outdoor temperature sensor (http://127.0.0.1/json.htm?type=devices&rid=idx_of_your_outdoor_temperature_device) and the json command for the indoor temperature sensor (http://127.0.0.1/json.htm?type=devices&rid=idx_of_your_indoor_temperature_device)
 11. Click "add"
 12. If all works well, 25 devices should have been added to the devices tab and you are now ready to use the plugin!
![image](https://user-images.githubusercontent.com/30364409/118498856-b8ae4100-b726-11eb-8a57-1d12cbe4ae94.png)

## How to use the plugin
1. 1st of all your need to configure your heating curve, by setting the setpoints "Boiler Temp at +20", "Boilertemp at -10" and the "Curvator" selector switch. See paragraph below on how to get to the correct curve. Here's an example (+20 settings = 20, -10 setting is 10) with the different curvature settings drawn into it to get an idea:
![image](https://user-images.githubusercontent.com/30364409/118477419-f010f380-b70e-11eb-9796-9752f7067d76.png)
    
2. Then there are additional setpoints you can configure to change the bevaviour
    - "Program": a selector in which you can choose wich porgram to run: Off (no programming, only manual), Day (Boiler temperature is based on heating cuver and reference room compensation), Night (Boiler is switched off, unless below night setpoint), Frost Protection (Boiler is switched off, unless temperature below fp setpoint)
    - "Temperature compensation": setting the parameters will make sure that if reference room temperature is below the "setpoint", the boiler temperature is raised with the difference in temperature, multiplied by the "Temperature compensation" setting. E.g. when you want it bo be 20 Celcius, but actual temp is 18 celcius en temperature compensation is set to 5 degrees Celcius, the boiler temperature will be raised with 10 degreees celcius
    - "Day Setpoint", "Night Setpoint", "Frost Protection Setpoint". The setpoint values to aim for in the different pograms
    - "Minimum Boiler Temperature" and "Maximum Boiler Temperature": No matter what the outcome of the calculations above. The boiler temperature will never exceed these values.
    - A "Holiday" switch: if this is set to "On", it will overrule any program and only make heating active when the reference room temperature drops below the frost protection setpoint
    - A "Daytime extension" switch: When this switch is on, it will override any program to and for the day program during the extension time which you can set in the plugin configuration afer which this button will be automaticall switched back to "Off". You can also use this switch during the "holiday" time to temperarily overrule the holiday program. 

3. And then there some devices to let you control the boiler directly
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

## Setting the  heating curve
Wheter your home heating will be comfortable without generating too much gas uses is entirely up to how well you finetuned the heating curve on your situation. Setting the heat curve might feel complex, I however found out that is it quite easy to get the correct heating curve if follow the following basic rules:
1. Start with the default values, they should be OK for a lot of situations. 
2. If it's not comfortable: act on it to make it comforable:
    - if it's too cold during warm weather: increase the setpoint for temperature at +20
    - if it's too cold during cold wather: increase the setpoint for temperature at -10 
    - if it's too cold in the middle of the heat curve (outside temperature around 10 degrees): Increase the curvature
    - if it's too warm during warm weather: decrease the setpoint for temperature at +20
    - if it's too warm during cold wather: decrease the setpoint for temperature at -10
    - if it's too warm in the middle of the heat curve (outside temperature around 10 degrees): Decrease the curvature 
    - if you house does not warmup fast enough: increase the reference room temperature compensation setting 
3. if it's always comfortable, try to save gas usage: 
    - try to decrease both setpoints (until you start loosing comfort)
    - try to lower the curvature (until you start loosing comfort)
    - try to decrease the reference room temperature compensation setting (until you start loosing comfort)

## Contributions
Last but not least: But if you would like extra features in this plugin, feel free to build them yourself, just as long as you make PR's, so other users can benefit from your enhancements as well

## Testing
At the moment of writing my opentherm interface was not yet deliverd, so everything is tested, but stubbed and i am still waiting to test again a real boiler ;-)

