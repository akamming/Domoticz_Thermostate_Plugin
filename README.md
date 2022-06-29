# Domoticz_Thermostate_Plugin
Domoticz Plugin for ESP thermostat with weather dependent heating control, but can also act like a normal thermostat based on inside temperature only.

## Why this plugin
My current boiler is end of life and i needed a new one. My current thermostate is already Weather Dependent, but cannot take advantage of the modulation features of a new boiler and i didn't like the limitations of all the commercial propositions of a smart weather dependent thermostate, so by creating one myself in domoticz I now have the following advantages:
1. lower cost for the same functionality as my old thermostat: 30 EUR of material against 300 EUR for a commercial system (and then i'm ignoring the fact that after initial price, some also need subscriptions)
2. fully opentherm compatible, with all advantages of a modern modulating system (many commercial weather dependent systems only support on/off protocol)
3. no private data (e.g. wheter or not i am at home) in a public cloud
4. Full control of the boiler if set to manual
5. All boiler sensors available in domoticz and the ability to send notification (e.g. on low water pressure)
6. Domoticz timers have much more options than the ones on commerical thermostats
7. No need for an expensive (also 100+ EUR) outside temperature connected to the boiler (any temperature device in domoticz can be used, so also owm or buienradar)
8. Full domoticz integration, so heating can be  part of scenes, scripts and other events
9. Easy switching between modulating thermostat or weather dependent mode

## Prerequisites
1. A wemos D1 with domoticz opentherm handler firmware (https://github.com/akamming/esp_domoticz_opentherm_handler)
2. Connected to an opentherm adapter (like http://ihormelnyk.com/opentherm_adapter)
3. which is connected to an opentherm compatible Boiler
4. A working domoticz installation with at least and make sure you know the IDX numbers of 
    - a working temperature device for measuring the outside temperature
    - a working temperature device for measuring the inside temperature in 1 room (the "reference room")

## installation
1. Install the custom firmware on Wemos D1, using instructions here (https://github.com/akamming/esp_domoticz_opentherm_handler) 
2. Connect the Wemos D1 to the opentherm adapter on pin 2 and 3
3. Connect the opentherm adapter to the boiler 
4. Prepare the Wemos D1 by 
    - powering on the device
    - connect with a device to WiFi Access Point "Thermostat"
    - browser to http://192.168.4.1 
    - follow instructions to connect the ESP to correct WiFi network
5. install this plugin into domoticz by     
   - cd your_domoticz_dit/plugins
   - download the release from the "releases" link, unzip the .zip in a new directory to your liking
   - or if you want alway want to have the latest updates: instead of downloading the release download directly from the reposity with "git clone https://github.com/akamming/Domoticz_Thermostate_Plugin/"   (later you can do git pull to get the latest updates) 
   - restart domoticz
   - go to hardware page. The plugin (Weather Dependent Heating Control) should now be visible in the "Type" dropdown
6. select the plugin, and enter the following config:
    - the hostname/ipadress and port of domoticz (mandatory, default works with standard domoticz installation), 
    - option username/password for domoticz (mandatory, in standard domoticz install, you can leave this empty) 
    - the  hostname / ip adres of your Wemos  (mandatory, in standard network config, domoticz can find the ESP using the default setting)
    - the IDX of the domoticz device which measures the outdoor temperature (mandatory)
    - idx IDX of the domoticz device which measures temperature in the reference room (mandatory)) 
    - and a duration for the "Daytime Extensions" button in minutes 
7. Click "add"
 
If all works well, several devices should have been added to the devices tab and you are now ready to use the plugin!
![image](https://user-images.githubusercontent.com/30364409/118498856-b8ae4100-b726-11eb-8a57-1d12cbe4ae94.png)

## How to use the plugin
1. 1st of all your need to configure your heating curve, by setting the setpoints "Boiler Temp at +20", "Boilertemp at -10" and the "Curvator" selector switch. See paragraph below on how to get to the correct curve. Here's an example (+20 settings = 20, -10 setting is 10) with the different curvature settings drawn into it to get an idea:
![image](https://user-images.githubusercontent.com/30364409/118477419-f010f380-b70e-11eb-9796-9752f7067d76.png)
    
2. Then there are additional setpoints you can configure to change the bevaviour
    - A "Fireplace / Weather Dependent Control": If switched on, the thermostate is in Weather Dependant Mode, meaning the outside temperature and the heating curve determines the temperature of the boiler. If switched off, the plugin will act like a normal thermostat, bringing the room to the right temperature based on internal temperature sensor only.
    - "Program": a selector in which you can choose wich porgram to run: Off (no programming, only manual), Day (Boiler temperature is based on heating cuver and reference room compensation), Night (Boiler is switched off, unless below night setpoint), Frost Protection (Boiler is switched off, unless temperature below fp setpoint)
    - "Temperature compensation": setting the parameters will make sure that if reference room temperature is below the "setpoint", the boiler temperature is raised with the difference in temperature, multiplied by the "Temperature compensation" setting. E.g. when you want it bo be 20 Celcius, but actual temp is 18 celcius en temperature compensation is set to 5 degrees Celcius, the boiler temperature will be raised with 10 degreees celcius
    - "Day Setpoint", "Night Setpoint", "Frost Protection Setpoint". The setpoint values to aim for in the different pograms
    - "Minimum Boiler Temperature" and "Maximum Boiler Temperature": No matter what the outcome of the calculations above. The boiler temperature will never exceed these values.
    - A "Holiday" switch: if this is set to "On", it will overrule any program and only make heating active when the reference room temperature drops below the frost protection setpoint
    - A "Daytime extension" switch: When this switch is on, it will override any program to and for the day program during the extension time which you can set in the plugin configuration afer which this button will be automaticall switched back to "Off". You can also use this switch during the "holiday" time to temperarily overrule the holiday program. 
    - A "DHW controlled by program" switch: When this switch is on, this forces the boiler DHW function to be on during daytime program and switched off during night or frost protection program.

3. And then there some devices to let you control the boiler directly
    - "Boiler Setpoint". When the program is Off, you can use this setpoint to manually set the boiler termpature
    - "DHW Setpoint". If you have a SWH system, you can use this setpoint to manually set the water temperature
    - "EnableCentralHeating". When the program is Off, you can use this switch to manually switch on or off the central heating
    - "EnableCooling", if your system supports and the program is set to Off: You can use this switch to manually switch on or off cooling
    - "EnableHotWater", if your system supports: You can use this switch to manually switch on or off the hotwater system

4. And then there is information reported about the boiler (not all sensors are supported by every boiler): 
    - "Central Heating": the reporting of opentherm if central heating is switched on
    - "Cooling": the reporting of opentherm if cooling is switched on
    - "HotWater": The reporting of opentherm if hotwater is switched on
    - "Flame": is the Flame on or Off
    - "Pressure": The pressure in the boiler
    - "Modulation": The modulationlevel of the boiler
    - "BoilerTemperature": The temperature of the boiler
    - "ReturnTemperature": The temperature of the water returning to the boiler
    - "DHWTemperature": The temperature of the hot water supply

5. All things work as regular domoticz devices, so you can use the "regular" domoticz magic to
    - add devices to your favorites or room definitions to create a GUI for the thermostast  
    - set timers on the "Program" to switch between day, night and frost protection programs  
    - set timers on the setpoints to get different levels of comfort during the day
    - set timers on the "Enable DHW" switch if you would like to save gas by switching off  
    - set alarms to alert you if if the waterpressure is dropping below a certain level and you want to refill before your boiler gets into an error state
    - make the buttons part of a scene to have the heating change as well in certain scenes
    - etc..etc... 

Have fun!

## Setting the  heating curve
Wheter your home heating will be comfortable without generating too much gas uses is entirely up to how well you finetuned the heating curve on your situation. Setting the heat curve might feel complex, I however found out that is it quite easy to get the correct heating curve if follow the following basic rules:
1. Start with the default values, they should be OK for a lot of situations. 
2. If it's not comfortable: act on it to make it comfortable:
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
If you would like to build extra features in this plugin, feel free to do so, just as long as you make PR's, so other users can benefit from your contributions as well

## Testing
Heating: i only have 1 type of boiler in my home ;-) it was replaced recently so i know it works on both boilers. But you have to check if it works with your boiler.
Cooling: I don't have a cooling system myself, so i could test the correct commands are sent to opentherm, but i could not check if it really works. Let me know if it does!
