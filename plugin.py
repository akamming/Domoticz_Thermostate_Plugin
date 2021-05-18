# OpenTherm Weather Dependent Heating Control
#
# Author: akamming
#
"""
<plugin key="OpenTherm" name="Weather Dependent Heating Control" author="akamming" version="1.0.0" wikilink="http://www.domoticz.com/wiki/plugins/plugin.html" externallink="https://github.com/akamming/esp_domoticz_opentherm_handler/">
    <description>
        <h2>Weather Dependent Heating Control</h2><br/>
        Use Domoticz to control your OpenTherm Boiler<br/>
        <br/>
        This plugin will make domoticz act as a thermostate, which will set the boiler temperature based on outside temperature, basically using a heating curve. If you want to know what a heating curve is, please look at articles like http://tech-controllers.com/blog/heating-curve---what-is-it-and-how-to-set-it<br/><br/>
        Requires a Wemos D1 with an opentherm adapter and domoticz helper firmware (https://github.com/akamming/esp_domoticz_opentherm_handler)<br/>
        <h3>Features</h3>
        <ul style="list-style-type:square">
            <li>Read your boiler sensors</li>
            <li>Control Heating, Cooling and Hot Water</li>
            <li>Set DHW setpoints</li>
            <li>Control Boiler Temperature based on outside temperature</li>
        </ul>
        <h3>Configuration</h3>
        Please fill the following coordinates to make this plugin work<br/>
        <ul style="list-style-type:square">
            <li>IP adress or hostname from the Wemos D1 containing the domoticz opentherm handler</li>
            <li>the json command to get your oudside temperature temperature</li>
            <li>the json command to get your reference room temperature, this is optional and is only needed if you want to use reference room compensation</li>
            <li>The number of minutes the "Daytime Extension" should be active when pressed</li>
        </ul>
    </description>
    <params>
        <param field="Mode1" label="Hostname/IP Adress" width="300px" required="true" default="" />
        <param field="Mode2" label="domoticz json url for outside temperature" default="http://127.0.0.1:8080/json.htm?type=devices&amp;rid=38" required="true" />
        <param field="Mode3" label="domoticz json url for reference room (inside) temperature" default="http://127.0.0.1:8080/json.htm?type=devices&amp;rid=39"/>
        <param field="Mode4" label="Daytime Extension Time in minutes" default="120"/>
    </params>
</plugin>
"""
import Domoticz
#from domoticz import Devices
import requests
import json
import datetime
import time

#Constants
RequiredInterface=1

#UnitID's
ENABLECENTRALHEATING=1
ENABLEHOTWATER=2
ENABLECOOLING=3
CENTRALHEATING=4
HOTWATER=5
COOLING=6
FLAME=7
BOILERSETPOINT=8
DHWSETPOINT=9
BOILERTEMPERATURE=10
DHWTEMPERATURE=11
RETURNTEMPERATURE=12
MODULATION=13
PRESSURE=14
BOILERTEMPATPLUS20=15
BOILERTEMPATMIN10=16
MAXBOILERTEMP=17
MINBOILERTEMP=18
SWITCHHEATINGOFFAT=19
PROGRAMSWITCH=20
CURVATURESWITCH=21
DAYSETPOINT=22
NIGHTSETPOINT=23
FROSTPROTECTIONSETPOINT=24
REFERENCEROOMCOMPENSATION=25
DAYTIMEEXTENSION=26
HOLIDAY=27
DHWCONTROL=28

#Global vars
Hostname=""
DayTimeExtensionTime=120
Debugging=True
#Debugging=False

def getInt(s):
    try: 
        int(s)
        return s
    except ValueError:
        return 0

def Debug(text):
    global Debug
    if (Debugging):
        Domoticz.Log("DEBUG: "+text)

def Log(text):
    Domoticz.Log(text)

def UpdateCustomSensor(SensorName,UnitID,Value):
       #Creating devices in case they aren't there...
        if not (UnitID in Devices):
            Debug("Creating device "+SensorName)
            Domoticz.Device(Name=SensorName, Unit=UnitID, TypeName="Custom", Used=1).Create()
        Devices[UnitID].Update(nValue=0, sValue=str(Value))
        Domoticz.Log("Counter ("+Devices[UnitID].Name+")")

def UpdatePercentageSensor(SensorName,UnitID,Value):
       #Creating devices in case they aren't there...
        if not (UnitID in Devices):
            Debug("Creating device "+SensorName)
            Domoticz.Device(Name=SensorName, Unit=UnitID, TypeName="Percentage", Used=1).Create()
        Devices[UnitID].Update(nValue=int(Value), sValue=str(Value))
        Domoticz.Log("Percentage ("+Devices[UnitID].Name+")")

def UpdateOnOffSensor(SensorName,UnitID,Value):
       #Creating devices in case they aren't there...
        if not (UnitID in Devices):
            Debug("Creating device "+SensorName)
            Domoticz.Device(Name=SensorName, Unit=UnitID, TypeName="Switch", Used=1).Create()
        newValue=0
        if (Value.lower()=="on"):
            newValue=1
        if newValue!=Devices[UnitID].nValue:
            Devices[UnitID].Update(nValue=newValue, sValue=str(Value))
            Domoticz.Log("Switch ("+Devices[UnitID].Name+")")

def UpdateSetpoint(SensorName,UnitID,Value):
       #Creating devices in case they aren't there...
        if not (UnitID in Devices):
            Debug("Creating device "+SensorName)
            Domoticz.Device(Name=SensorName, Unit=UnitID, Type=242, Subtype=1, Used=1).Create()
        if int(Value)!=Devices[UnitID].nValue:
            Devices[UnitID].Update(nValue=int(Value), sValue=str(Value))
            Domoticz.Log("Setpoint ("+Devices[UnitID].Name+")")

def UpdateTemperatureSensor(SensorName,UnitID,Value):
       #Creating devices in case they aren't there...
        if not (UnitID in Devices):
            Debug("Creating device "+SensorName)
            Domoticz.Device(Name=SensorName, Unit=UnitID, TypeName="Temperature", Used=1).Create()
        Devices[UnitID].Update(nValue=int(Value), sValue=str(Value))
        Domoticz.Log("Temperature ("+Devices[UnitID].Name+")")

def UpdatePressureSensor(SensorName,UnitID,Value):
       #Creating devices in case they aren't there...
        if not (UnitID in Devices):
            Debug("Creating device "+SensorName)
            Domoticz.Device(Name=SensorName, Unit=UnitID, TypeName="Pressure", Used=1).Create()
        Devices[UnitID].Update(nValue=int(Value), sValue=str(Value))
        Domoticz.Log("Pressure ("+Devices[UnitID].Name+")")

def UpdateSensors(data):
    #Update steering vars
    UpdateOnOffSensor("EnableCentralHeating",ENABLECENTRALHEATING,data["EnableCentralHeating"])
    UpdateOnOffSensor("EnableHotWater",ENABLEHOTWATER,data["EnableHotWater"])
    UpdateOnOffSensor("EnableCooling",ENABLECOOLING,data["EnableCooling"])
    UpdateSetpoint("BoilerSetpoint",BOILERSETPOINT,data["BoilerSetpoint"])
    UpdateSetpoint("DHWSetpoint",DHWSETPOINT,data["DHWSetpoint"])

    #Update Sensors
    if data["OpenThermStatus"]=="OK":
        UpdateOnOffSensor("CentralHeating",CENTRALHEATING,data["CentralHeating"])
        UpdateOnOffSensor("HotWater",HOTWATER,data["HotWater"])
        UpdateOnOffSensor("Cooling",COOLING,data["Cooling"])
        UpdateOnOffSensor("Flame",FLAME,data["Flame"])
        UpdateTemperatureSensor("BoilerTemperature",BOILERTEMPERATURE,data["BoilerTemperature"])
        UpdateTemperatureSensor("DHWTemperature",DHWTEMPERATURE,data["DhwTemperature"])
        UpdateTemperatureSensor("ReturnTemperature",RETURNTEMPERATURE,data["ReturnTemperature"])
        UpdatePressureSensor("Pressure",PRESSURE,data["Pressure"]) 
        UpdatePercentageSensor("Modulation",MODULATION,data["Modulation"])
    else:
        Log("Communication Error between ESP and Boiler: "+data["OpenThermStatus"])

def CreateSetPoint(SensorName,UnitID,DefaultValue):
    if not (UnitID in Devices):
        Debug("Creating setpoint "+SensorName)
        Domoticz.Device(Name=SensorName, Unit=UnitID, Type=242, Subtype=1, Used=1).Create()
        Devices[UnitID].Update(nValue=int(DefaultValue), sValue=str(DefaultValue))

def CreateOnOffDevice(SensorName,UnitID,DefaultValue):
    if not (UnitID in Devices):
        Debug("Creating on/off device "+SensorName)
        Domoticz.Device(Name=SensorName, Unit=UnitID, TypeName="Switch", Used=1).Create()
        nv=0
        if DefaultValue.lower()=="on":
            nv=1
            Devices[UnitID].Update(nValue=nv, sValue=str(DefaultValue))

def CreateCurvatureSwitch():
    if not (CURVATURESWITCH in Devices):
        Debug("Creating Curvature selector switch")
        Options = {"LevelActions": "|| ||", 
                   "LevelNames": "None|Small|Medium|Large",
                   "LevelOffHidden": "false",
                   "SelectorStyle": "1"}
        Domoticz.Device(Name="Curvature", Unit=CURVATURESWITCH, TypeName="Selector Switch", Options=Options, Used=1).Create()

def CreateProgramSwitch():
    if not (PROGRAMSWITCH in Devices):
        Debug("Creating program switch")
        Options = {"LevelActions": "|| ||", 
                   "LevelNames": "Off|Frost Proctection|Night|Day",
                   "LevelOffHidden": "false",
                   "SelectorStyle": "1"}
        Domoticz.Device(Name="Program", Unit=PROGRAMSWITCH, TypeName="Selector Switch", Options=Options, Used=1).Create()

def CreateOnOffSwitch(SensorName,UnitID):
       #Creating devices in case they aren't there...
        if not (UnitID in Devices):
            Debug("Creating switch "+SensorName)
            Domoticz.Device(Name=SensorName, Unit=UnitID, TypeName="Switch", Used=1).Create()

def CreateParameters():
    CreateSetPoint("Boiler Temp at +20",BOILERTEMPATPLUS20,20)
    CreateSetPoint("Boiler Temp at -10",BOILERTEMPATMIN10,70)
    CreateSetPoint("Maximum Boiler Temperature",MAXBOILERTEMP,90)
    CreateSetPoint("Minimum Boiler Temperature",MINBOILERTEMP,20)
    CreateSetPoint("SwitchHeatingOffAt",SWITCHHEATINGOFFAT,17)
    CreateProgramSwitch()
    CreateCurvatureSwitch()
    CreateSetPoint("Day Setpoint",DAYSETPOINT,20)
    CreateSetPoint("Night Setpoint",NIGHTSETPOINT,15)
    CreateSetPoint("Frost Protection Setpoint",FROSTPROTECTIONSETPOINT,7)
    CreateSetPoint("Reference Room Temperature Compensation",REFERENCEROOMCOMPENSATION,3)
    CreateOnOffSwitch("DayTimeExtension",DAYTIMEEXTENSION)
    CreateOnOffSwitch("Holiday",HOLIDAY)
    CreateOnOffSwitch("DHW controlled by program",DHWCONTROL)

def ProcessResponse(data):
    Debug("ProcessResponse()")
    ifversion=0;
    #for x in data:
    #    Debug("Value "+x+" is "+str(data[x]))
    try:
        ifversion=data["InterfaceVersion"]
    except:
        Log("ERROR: Could not get InterfaceVersion")

    if ifversion==RequiredInterface:
        #Debug("We have the correct interface")
        UpdateSensors(data)
    else:
        Log("Error Interace version "+RequiredInterface+" required, make sure you have latest plugin and firmware")



def ESPCommand(url):
    Debug("Calling "+Hostname+url)
    try:
        response = requests.get(Hostname+url, timeout=3)
        if (response.status_code==200):
            Debug("Call succeeded")
            ProcessResponse(response.json())
        else:
            Log("ERROR: unable to contact ESP on "+url+", statuscode="+str(response.status_code))
    except:
        Log("Error: Unable to call "+url)

def getSensors():
    Debug("Get Sensors()")
    ESPCommand("GetSensors")

def DeriveTargetTemperatureFromHeatingCurve(CurrentOutsideTemperature):
    #Calculate temperature
    TargetTemperature=0

    if (CurrentOutsideTemperature>20):
        #when above 20 degrees, use minimum termpature from heating curve
        TargetTemperature=Devices[BOILERTEMPATPLUS20].nValue
    else:
        Curvature=Devices[CURVATURESWITCH].nValue/10+1
        MaxYDelta=Devices[BOILERTEMPATMIN10].nValue-Devices[BOILERTEMPATPLUS20].nValue #boilertemp at -10 minus boilertemp at +20
        MaxXDelta=30 # 20 - (-10)=30
        MaxToReach=MaxYDelta**Curvature
        TargetTemperature=((20-CurrentOutsideTemperature)/MaxXDelta*(MaxToReach))**(1/Curvature)+Devices[BOILERTEMPATPLUS20].nValue
        Debug("Curvature = "+str(Curvature)+", MaxYDelta="+str(MaxYDelta))
    Debug("Calculated temperature according to heating curve: "+str(TargetTemperature))

    #Perform reference room compensation if 
    Debug("Checking for room temperature compensation")
    Compensation=Devices[REFERENCEROOMCOMPENSATION].nValue
    if Compensation>0:
        Succes,CurrentInsideTemperature=GetTemperature(Parameters["Mode3"])
        temperaturetoreach=0
        if Succes:
            #check to which target to get
            if Devices[PROGRAMSWITCH].nValue==30:
                temperaturetoreach=Devices[DAYSETPOINT].nValue
            elif Devices[PROGRAMSWITCH].nValue==20:
                temperaturetoreach=Devices[NIGHTSETPOINT].nValue
            elif Devices[PROGRAMSWITCH].nValue==10:
                temperaturetoreach=Devices[FROSTPROTECTIONSETPOINT].nValue
            else:
                Log("This code should not be reached, settings parameters to disable compensation")
                temperaturetoreach=20
                Compensation=0

            if CurrentInsideTemperature<temperaturetoreach:
                Debug("Applying reference room temperature compensation: "+str((temperaturetoreach-CurrentInsideTemperature)*Compensation))
                TargetTemperature+=(temperaturetoreach-CurrentInsideTemperature)*Compensation
            else:
                Debug("temperature above setpoint, no reference room compensation")
    
    #Checking max parameters
    if TargetTemperature>Devices[MAXBOILERTEMP].nValue:
        Debug("Calculated temp above max temp, correcting")
        TargetTemperature=Devices[MAXBOILERTEMP].nValue

    #Checking mn parameters
    if TargetTemperature<Devices[MINBOILERTEMP].nValue:
        Debug("Calculated temp below min temp, correcting")
        TargetTemperature=Devices[MINBOILERTEMP].nValue

    return TargetTemperature

def GetTemperature(url):
    try:
        Debug("Retrieving "+url)
        response = requests.get(url)
        if response.status_code==200:
            #we have a succesful http call, let's try to interpret
            data = response.json()
            if (data["status"]=="OK"):
                #All is OK, read temperature
                CurrentTemperature=data["result"][0]["Temp"]
                Debug("Current Temperature is "+str(CurrentTemperature))
                return True,CurrentTemperature
            else:
                #Domoticz Error
                Log("domoticz error getting temperature "+response.status_code+" : "+response.text+", unable to execute program")
                return False,0
        else:
            #HTTP error
            Log("domoticz error getting temperature "+response.status_code+" : "+response.text+", unable to execute program")
            return False,0
    except:
        #Exception
        Log("Error: Unable to get temperature on "+url)
        return False,0


class BasePlugin:
    enabled = False
    def __init__(self):
        #self.var = 123
        return

    def onStart(self):
        global Hostname
        global OutsideTemperatureIdx
        global InsideTemperatureIdx
        global DayTimeExtensionTime

        Debug("onStart called")
       
        # Read config
        #for  x in Parameters:
        #    Debug("Paramater "+x+" is "+str(Parameters[x]))
        Hostname="http://"+Parameters["Mode1"]+"/" 
        Debug("Connection will be made to "+Hostname)

        DayTimeExtensionTime=int(Parameters["Mode4"])
        Debug("Daytime Extension Time = "+str(DayTimeExtensionTime))

        #Create parameter setpoints
        CreateParameters()

        #Update Devices
        getSensors()

    def onStop(self):
        Debug("onStop called")

    def onConnect(self, Connection, Status, Description):
        Debug("onConnect called")

    def onMessage(self, Connection, Data):
        Debug("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        #if Unit==in {CURVATURESWITCH or Unit==PROGRAMSWITCH:
        if Unit in {CURVATURESWITCH,PROGRAMSWITCH,MINBOILERTEMP,MAXBOILERTEMP,BOILERTEMPATMIN10,BOILERTEMPATPLUS20,SWITCHHEATINGOFFAT,
                DAYSETPOINT,NIGHTSETPOINT,FROSTPROTECTIONSETPOINT,REFERENCEROOMCOMPENSATION}:
            Devices[Unit].Update(nValue=int(Level), sValue=str(Level))
        elif Unit in {HOLIDAY,DAYTIMEEXTENSION,DHWCONTROL}:
            NewValue=0
            if Command=="On":
                NewValue=1
            Devices[Unit].Update(nValue=NewValue, sValue=Command)
        elif Unit==ENABLECENTRALHEATING:
            if Command.lower()=="on":
                ESPCommand("EnableCentralHeating")
            else:
                ESPCommand("DisableCentralHeating")
        elif Unit==ENABLEHOTWATER:
            if Command.lower()=="on":
                ESPCommand("EnableHotWater")
            else:
                ESPCommand("DisableHotWater")
        elif Unit==ENABLECOOLING:
            if Command.lower()=="on":
                ESPCommand("EnableCooling")
            else:
                ESPCommand("DisableCooling")
        elif Unit==BOILERSETPOINT:
            ESPCommand("SetBoilerTemp?Temperature="+str(Level))
        elif Unit==DHWSETPOINT:
            ESPCommand("SetDHWTemp?Temperature="+str(Level))
        else: 
            Debug("Unhandle command")

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Debug("onDisconnect called")

    def onHeartbeat(self):
        Debug("onHeartbeat called")

        if Devices[PROGRAMSWITCH].nValue==0:
            #Program inactive, just get sensors
            Debug("Program inactive")
            getSensors()
        else:
            #Program Active, try to get outside temperature
            Succes,CurrentOutsideTemperature=GetTemperature(Parameters["Mode2"])
            if Succes:
                Debug("Current Outside Temperature is "+str(CurrentOutsideTemperature))

                #Calculate desired boiler temperature
                TargetTemperature=DeriveTargetTemperatureFromHeatingCurve(CurrentOutsideTemperature)
                
                if (Devices[PROGRAMSWITCH].nValue==30 and Devices[HOLIDAY].nValue==0) or Devices[DAYTIMEEXTENSION].nValue==1:
                    #check if we have to deactivate extension
                    if Devices[DAYTIMEEXTENSION].nValue==1:
                        Debug("Day time extension active ["+Devices[DAYTIMEEXTENSION].LastUpdate+"]")
                        res = datetime.datetime(*(time.strptime(Devices[DAYTIMEEXTENSION].LastUpdate, "%Y-%m-%d %H:%M:%S")[0:6]))
                        delta=(datetime.datetime.now()-res).total_seconds()
                        Debug("button was pressed "+str(int(delta))+"seconds ago,"+str(int(DayTimeExtensionTime*60-delta))+" to switch back program again")
                        if (delta>DayTimeExtensionTime*60):
                            Log("DaytimeExtension expired, going back to normal program")
                            UpdateOnOffSensor("DayTime Extension",DAYTIMEEXTENSION,"Off")
                    Debug("Handling Day program")
                    #Manage Heating
                    if CurrentOutsideTemperature>(Devices[SWITCHHEATINGOFFAT].nValue):
                        Debug("Temp aboven day treshold")
                        #We are at the temperature at which we can switchoff heating
                        if Devices[ENABLECENTRALHEATING].nValue==1:
                            Log("Above temperature treshold, switching off boiler")
                            ESPCommand("DisableCentralHeating")
                        else:
                            ESPCommand("GetSensors")
                    else:
                        #Make sure central heating is switched on
                        if Devices[ENABLECENTRALHEATING].nValue==0:
                            Log("Switching on the boiler")
                            ESPCommand("EnableCentralHeating")
                        #Send command for boilertermperature
                        ESPCommand("SetBoilerTemp?Temperature="+str(TargetTemperature))
                    #Manage DHW
                    if Devices[DHWCONTROL].nValue==1:
                        if  Devices[ENABLEHOTWATER].nValue==0:
                            Log("Switching on DHW")
                            ESPCommand("EnableHotWater")
                elif Devices[PROGRAMSWITCH].nValue==10 or Devices[HOLIDAY].nValue==1:
                    if Devices[HOLIDAY].nValue==1:
                        Debug("Holiday program active")
                    Debug("Handling Frost protection program")
                    #Manage DHW
                    if Devices[DHWCONTROL].nValue==1:
                        if  Devices[ENABLEHOTWATER].nValue==1:
                            Log("Switching off DHW")
                            ESPCommand("DisableHotWater")
                    #Manage Heating
                    Succes,CurrentInsideTemperature=GetTemperature(Parameters["Mode3"])
                    if Succes:
                        Debug("Current inside temperature = "+str(CurrentInsideTemperature))
                        if CurrentInsideTemperature<Devices[FROSTPROTECTIONSETPOINT].nValue:
                            #temperature too low, make there is heating
                            #Check if we have to enable the central heating
                            if Devices[ENABLECENTRALHEATING].nValue==0:
                                Log("Enable heating on the boiler")
                                ESPCommand("EnableCentralHeating")
                            #Send command
                            ESPCommand("SetBoilerTemp?Temperature="+str(TargetTemperature))
                        else:
                            #above or on setpoint, Heating can be switched off
                            if Devices[ENABLECENTRALHEATING].nValue==1:
                                Log("Disable heating on the boiler")
                                ESPCommand("DisableCentralHeating")
                            ESPCommand("GetSensors")
                    else:
                        Debug("Unable to execute Frost Protection program, no inside temperature")
                elif Devices[PROGRAMSWITCH].nValue==20:
                    Debug("Handling Night Program")
                    #Manage DHW
                    if Devices[DHWCONTROL].nValue==1:
                        if  Devices[ENABLEHOTWATER].nValue==1:
                            Log("Switching off DHW")
                            ESPCommand("DisableHotWater")
                    #Manage Heating
                    Succes,CurrentInsideTemperature=GetTemperature(Parameters["Mode3"])
                    if Succes:
                        Debug("Current inside temperature = "+str(CurrentInsideTemperature))
                        if CurrentInsideTemperature<Devices[NIGHTSETPOINT].nValue:
                            #temperature too low, make there is heating
                            #Check if we have to enable the central heating
                            if Devices[ENABLECENTRALHEATING].nValue==0:
                                Log("Enable heating on the boiler")
                                ESPCommand("EnableCentralHeating")
                            #Send command
                            ESPCommand("SetBoilerTemp?Temperature="+str(TargetTemperature))
                        else:
                            #above or on setpoint, Heating can be switched off
                            if Devices[ENABLECENTRALHEATING].nValue==1:
                                Log("Disable heating on the boiler")
                                ESPCommand("DisableCentralHeating")
                            ESPCommand("GetSensors")
                    else:
                        Debug("Unable to execute night program, no inside temperature")
                    
                else:
                    Debug("Unknow value of program switch: "+str(Devices[PROGRAMSWITCH].nValue))
            else:
                Debug("no outside temperature, could not execute program")

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Settings:
        Debug("Setting "+str(x)+" is "+str(Settings[x]))
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return
