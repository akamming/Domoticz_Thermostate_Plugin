# Domoticz_Thermostate_Plugin
Domoticz Plugin for ESP thermostat with weather dependent heating control, but can also act like a normal thermostat based on inside temperature only.


## Warning for this version
This plugin is nog longer maintained: The functionality of the plugin is now moved to the firmware (https://github.com/akamming/esp_domoticz_opentherm_handler) which exposes the same devices to domoticz (but now also Home Assistant) as this plugin does, rendering this plugin obsolete.

So if you still use this plugin: Please start using Climate Setpoint which is exposed by the custom firmware and you can stop using this plugin (and still enjoy the same functionality).

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
1. A wemos D1 with domoticz opentherm handler latest firmware installed (https://github.com/akamming/esp_domoticz_opentherm_handler) with MQTT enabled
2. Connected to an opentherm adapter (like http://ihormelnyk.com/opentherm_adapter)
3. which is connected to an opentherm compatible Boiler
4. A working domoticz installation with MQTT autodiscovery enabled (so it disovers the Wemos D1 with the openthermhandler firmware) 

## installation
1. Make sure you have the correct devices in domoticz to handle you boiler. E.G. by using the ESP firmware on an ESP8266 together with an opentherm adatper: (https://github.com/akamming/esp_domoticz_opentherm_handler) in combination 
2. install this plugin into domoticz by     
   - cd your_domoticz_dit/plugins
   - download the release from the "releases" link, unzip the .zip in a new directory to your liking
   - or if you want alway want to have the latest updates: instead of downloading the release download directly from the reposity with "git clone https://github.com/akamming/Domoticz_Thermostate_Plugin/"   (later you can do git pull to get the latest updates) 
   - restart domoticz
   - go to hardware page. The plugin (Weather Dependent Heating Control) should now be visible in the "Type" dropdown
3. select the plugin, and enter the following config:
    - the hostname/ipadress and port of domoticz (mandatory, default works with standard domoticz installation), 
    - option username/password for domoticz (mandatory, in standard domoticz install, you can leave this empty) 
    - the IDX numbers of your domotica needed devices (separated with a comma). These device are created automatically if you use the referenced ESP8266 firmware 
       - Inside temperature: a temperature device for your inside temperature (used for modulating thermostat mode)
       - Outside temperature: a temperature device for your outside temperature (used for weather dependent mode)
       - Heating Active: a switch which reports "ON" when heating is active
       - Cooling Active: a switch which reports "ON" when cooling is active
       - HotWater Active: a switch which reports "ON" when the boiler is in HotWater heating mode
       - EnableHeating: a switch which tells the boiler to switch on heating mode
       - EnableCooling: a switch which tells the system to switch on cooling mode
       - BoilerSetpoint: a setpoint device which sets the to be acquired boiler temperature
    - and a duration for the "Daytime Extensions" button in minutes 
7. Click "add"
 
If all works well, several devices should have been added to the devices tab and you are now ready to use the plugin!
![image](https://user-images.githubusercontent.com/30364409/118498856-b8ae4100-b726-11eb-8a57-1d12cbe4ae94.png)

## How to use the plugin
1. If you plan to use Weather Dependent mode: your need to configure your heating curve, by setting the setpoints "Boiler Temp at +20", "Boilertemp at -10" and the "Curvator" selector switch. See paragraph below on how to get to the correct curve. Here's an example (+20 settings = 20, -10 setting is 10) with the different curvature settings drawn into it to get an idea:
![image](https://user-images.githubusercontent.com/30364409/118477419-f010f380-b70e-11eb-9796-9752f7067d76.png)
    
2. Then there are additional setpoints you can configure to change the bevaviour
    - A "Fireplace / Weather Dependent Control": If switched on, the thermostate is in Weather Dependant Mode, meaning the outside temperature and the heating curve determines the temperature of the boiler. If switched off, the plugin will act like a normal thermostat, bringing the room to the right temperature based on internal temperature sensor only.
    - "Program": a selector in which you can choose wich porgram to run: Off (no programming, only manual), Heating (only control heating), Cooling (only control cooling) & Auto (automatically choose between heating & cooling)  
    - "Temperature compensation": setting the parameters will make sure that if reference room temperature is below the "setpoint", the boiler temperature is raised with the difference in temperature, multiplied by the "Temperature compensation" setting. E.g. when you want it bo be 20 Celcius, but actual temp is 18 celcius en temperature compensation is set to 5 degrees Celcius, the boiler temperature will be raised with 10 degreees celcius
    - "Day Setpoint" & "Frost Protection Setpoint". The setpoint values to aim for in the different pograms
    - "Minimum Boiler Temperature" and "Maximum Boiler Temperature": No matter what the outcome of the calculations above. The boiler temperature will never exceed these values.
    - "Minimum Temperature Difference": Only enable heating cooling when temperature difference between boiler setpoint and heating/cooling > this value (saves energy. But don't set value too high, cause then room temp will fluctuate too much)
    - A "Holiday" switch: if this is set to "On", it will overrule any program and only make heating active when the reference room temperature drops below the frost protection setpoint
    - A "Daytime extension" switch: When this switch is on, it will override any program to and for the day program during the extension time which you can set in the plugin configuration afer which this button will be automaticall switched back to "Off". You can also use this switch during the "holiday" time to temperarily overrule the holiday program. 
    - A "heating / cooling" switch: This reports the mode of the boiler: Off, Heating or Cooling

3. All things work as regular domoticz devices, so you can use the "regular" domoticz magic to
    - add devices to your favorites or room definitions to create a GUI for the thermostast  
    - set timers on the "Program" to switch between day, night and frost protection programs  
    - set timers on the setpoints to get different levels of comfort during the day
    - make the buttons part of a scene to have the heating change as well in certain scenes
    - etc..etc... 
    
4. Bonus: In combination with the referenced ESP firmware you even have all devices to make a very nice thermostat device in homekit if you use the "Homebridge Domoticz Thermostat" plugin in homekit. Just look for this plugin in the hombebridge GUI. In this plugin you can configure the "Day setpoint" (what temperature you want the room to be), the "program" switch to set correct program and the "heating cooling" switch to make homekit show the correct state (and ofcourse add an internal temperature device to show your inside temperature in the homekit thermostat)  

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

## Rel 2 important notes
Some changes in the sensors to enable homekit (in combination with the homebridge plugin) compatibility
- The behaviour of the program switch changed from Off/Day/Night/Frostprotection to Off/Heating/Cooling/Auto 
- The Night Setpoint is gone, 
- a new selector switch (heating/cooling/off) was introduced to indicate whether the system is heating, cooling or off 
so if you created rules or macro's make sure they are changed as well when installing this release
