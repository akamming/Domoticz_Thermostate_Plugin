# OpenTherm Weather Dependent Heating Control
#
# Author: akamming
#
"""
<plugin key="OpenThermWDHC" name="OpenTherm Weather Dependent Heating Control" author="akamming" version="1.0.0" wikilink="https://github.com/akamming/Domoticz_Thermostate_Plugin#readme" externallink="https://github.com/akamming/esp_domoticz_opentherm_handler/">
    <description>
        <h2>Weather Dependent Heating Control</h2><br/>
        Use Domoticz to control your OpenTherm Boiler<br/>
        <br/>
        This plugin will make domoticz act as a OpenTherm Weather Dependent Thermostate. So a heating curve will determine boiler water temperatures, to get the right amount of heating ins all rooms of your building. If you want to know what a heating curve is, please look at articles like http://tech-controllers.com/blog/heating-curve---what-is-it-and-how-to-set-it<br/><br/>
        The description on how to use this plugin, can be found on <a href="https://github.com/akamming/Domoticz_Thermostate_Plugin#readme">the github page</a><br/>
        <h3>Configuration</h3>
        Please fill the following coordinates to make this plugin work<br/>
        <ul style="list-style-type:square">
            <li>Domticz IP adress and port (the default should work on a standard domoticz config)</li>
            <li>IP adress or hostname from the Wemos D1 containing the domoticz opentherm handler (the default should work on a standard network config)</li>
            <li>the IDX values of your outdoor and indoor temperature devices</li>
            <li>The number of minutes the "Daytime Extension" button should be active when pressed</li>
        </ul>
    </description>
    <params>
        <param field="Address" label="Domoticz IP Address" width="200px" required="true" default="localhost"/>
        <param field="Port" label="Domoticz Port" width="40px" required="true" default="8080"/>
        <param field="Username" label="Domoticz Username" width="200px" required="false" default=""/>
        <param field="Password" label="Domoticz Password" width="200px" required="false" default=""/>
        <param field="Mode1" label="ESP Hostname" default="domesphelper.local" width="200px" required="true"  />
        <param field="Mode2" label="idx for outside temperature device" default="514" width="100px" required="true" />
        <param field="Mode3" label="idx for reference room temperature device" default="685" width="100px" required="true" />
        <param field="Mode4" label="Daytime Extension Time in minutes" default="120" required="true" />
    </params>
</plugin>
"""
import Domoticz
import requests
import json
import datetime
import time
import urllib.parse as parse
import urllib.request as request
import base64 
import math
import os

#TODO: 

#Constants
RequiredInterface=2
SwitchOffHeatingDelta=1  #Switch off heating is current temp is more than this number of agrees above setpoint

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
THERMOSTATTEMPERATURE=29
FAULT=30
DIAGNOSTIC=31
FAULTCODE=32
DHWFLOW=33
OUTSIDETEMPERATURE=34
FPWD=35

#Global vars
Hostname=""
DayTimeExtensionTime=120
Debugging=False

#Vars for thermostat function
LastInsideTemperatureValue=0 #Remember last temp to calc difference
LastInsideTemperatureTimestamp=0

ierr = 0 #Remember Integral Error



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
        if float(Devices[UnitID].sValue)!=float(Value):
            Devices[UnitID].Update(nValue=0, sValue=str(Value))
            Domoticz.Log("Custom ("+Devices[UnitID].Name+")")

def UpdatePercentageSensor(SensorName,UnitID,Value):
        #Creating devices in case they aren't there...
        if not (UnitID in Devices):
            Debug("Creating device "+SensorName)
            Domoticz.Device(Name=SensorName, Unit=UnitID, TypeName="Percentage", Used=1).Create()
        if float(Devices[UnitID].sValue)!=float(Value):
            Devices[UnitID].Update(nValue=int(Value), sValue=str(Value))
            Domoticz.Log("Percentage ("+Devices[UnitID].Name+")")

def UpdateOnOffSensor(SensorName,UnitID,Value):
        #Creating devices in case they aren't there...
        if not (UnitID in Devices):
            Debug("Creating device "+SensorName)
            Domoticz.Device(Name=SensorName, Unit=UnitID, TypeName="Switch", Used=1).Create()
        newValue=0
        if (Value.lower()=="on" or Value.lower()=="yes"):
            newValue=1
        if newValue!=Devices[UnitID].nValue:
            Devices[UnitID].Update(nValue=newValue, sValue=str(Value))
            Domoticz.Log("Switch ("+Devices[UnitID].Name+")")

def UpdateSetpoint(SensorName,UnitID,Value):
        #Creating devices in case they aren't there...
        if not (UnitID in Devices):
            Debug("Creating device "+SensorName)
            Domoticz.Device(Name=SensorName, Unit=UnitID, Type=242, Subtype=1, Used=1, Image=15).Create()
        try:
            if float(Devices[UnitID].sValue)!=float(Value):
                Devices[UnitID].Update(nValue=int(Value), sValue=str(Value))
                Domoticz.Log("Setpoint ("+Devices[UnitID].Name+")")
        except:
            Domoticz.Log("Error comparing setpoint values")

def UpdateTemperatureSensor(SensorName,UnitID,Value):
        #Creating devices in case they aren't there...
        if not (UnitID in Devices):
            Debug("Creating device "+SensorName)
            Domoticz.Device(Name=SensorName, Unit=UnitID, TypeName="Temperature", Used=1).Create()
        try:
            if float(Devices[UnitID].sValue)!=float(Value):
                Devices[UnitID].Update(nValue=int(Value), sValue=str(Value))
                Domoticz.Log("Temperature ("+Devices[UnitID].Name+")")
        except:
            Domoticz.Log("Error updating temperature")

def UpdatePressureSensor(SensorName,UnitID,Value):
       #Creating devices in case they aren't there...
        if not (UnitID in Devices):
            Debug("Creating device "+SensorName)
            Domoticz.Device(Name=SensorName, Unit=UnitID, TypeName="Pressure", Used=1).Create()
        if float(Devices[UnitID].sValue)!=float(Value):
            Devices[UnitID].Update(nValue=int(Value), sValue=str(Value))
            Domoticz.Log("Pressure ("+Devices[UnitID].Name+")")

def UpdateSensors(data):
    #Debug("Update steering vars")
    UpdateOnOffSensor("EnableCentralHeating",ENABLECENTRALHEATING,data["EnableCentralHeating"])
    UpdateOnOffSensor("EnableHotWater",ENABLEHOTWATER,data["EnableHotWater"])
    UpdateOnOffSensor("EnableCooling",ENABLECOOLING,data["EnableCooling"])
    UpdateSetpoint("BoilerSetpoint",BOILERSETPOINT,data["BoilerSetpoint"])
    UpdateSetpoint("DHWSetpoint",DHWSETPOINT,data["DHWSetpoint"])
    UpdateTemperatureSensor("Thermostat Temperature",THERMOSTATTEMPERATURE,data["ThermostatTemperature"])

    #Update Sensors
    if data["OpenThermStatus"]=="OK":
        UpdateOnOffSensor("CentralHeating",CENTRALHEATING,data["CentralHeating"])
        UpdateOnOffSensor("HotWater",HOTWATER,data["HotWater"])
        UpdateOnOffSensor("Cooling",COOLING,data["Cooling"])
        UpdateOnOffSensor("Flame",FLAME,data["Flame"])
        UpdateOnOffSensor("Fault",FAULT,data["Fault"])
        UpdateOnOffSensor("Diagnostic",DIAGNOSTIC,data["Diagnostic"])
        UpdateTemperatureSensor("BoilerTemperature",BOILERTEMPERATURE,data["BoilerTemperature"])
        UpdateTemperatureSensor("DHWTemperature",DHWTEMPERATURE,data["DhwTemperature"])
        UpdateTemperatureSensor("ReturnTemperature",RETURNTEMPERATURE,data["ReturnTemperature"])
        UpdateTemperatureSensor("OutsideTemperature",OUTSIDETEMPERATURE,data["OutsideTemperature"])
        UpdatePressureSensor("Pressure",PRESSURE,data["Pressure"]) 
        UpdatePercentageSensor("Modulation",MODULATION,data["Modulation"])
        UpdateCustomSensor("FaultCode",FAULTCODE,data["FaultCode"])
    else:
        Log("Communication Error between ESP and Boiler: "+data["OpenThermStatus"])

def CreateSetPoint(SensorName,UnitID,DefaultValue):
    if not (UnitID in Devices):
        Debug("Creating setpoint "+SensorName)
        Domoticz.Device(Name=SensorName, Unit=UnitID, Type=242, Subtype=1, Used=1, Image=15).Create()
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
                   "SelectorStyle": "0"}
        Domoticz.Device(Name="Curvature", Unit=CURVATURESWITCH, TypeName="Selector Switch", Options=Options, Used=1).Create()

def CreateProgramSwitch():
    if not (PROGRAMSWITCH in Devices):
        Debug("Creating program switch")
        Options = {"LevelActions": "|| ||", 
                   "LevelNames": "Off|Frost Proctection|Night|Day",
                   "LevelOffHidden": "false",
                   "SelectorStyle": "0"}
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
    CreateOnOffSwitch("FirePlace/Weather Dependent Control",FPWD)

def ProcessResponse(data):
    ifversion=0;
    #for x in data:
     #   Debug("Value "+x+" is "+str(data[x]))
    try:
        ifversion=data["InterfaceVersion"]
    except:
        Log("ERROR: Could not get InterfaceVersion")

    if ifversion==RequiredInterface:
        UpdateSensors(data)
    else:
        Log("Error Interace version "+str(RequiredInterface)+" required, make sure you have latest plugin and firmware")



def ESPCommand(url):
    Debug("Calling "+Hostname+url)
    try:
        #response = requests.get(Hostname+url, timeout=3)
        response = requests.get(Hostname+url)
        if (response.status_code==200):
            ProcessResponse(response.json())
        else:
            Log("ERROR: unable to contact ESP on "+url+", statuscode="+str(response.status_code))
    except requests.exceptions.Timeout:
        Log("Error: Unable to call "+url+", due to timeout")
    except requests.exceptions.TooManyRedirects:
        Log("Error: Unable to call "+url+", due to too many redirects")
    except requests.exceptions.RequestException as e:
        Log("Error: Unable to call "+url+", due to exception ("+str(e)+")")
    #except:
    #    Log("Error: Unable to call "+url)

def getSensors():
    ESPCommand("GetSensors")

def CalculateBoilerSetPoint():
    global LastInsideTemperatureValue
    global LastInsideTemperatureTimestamp
   

    #Calculate temperature
    TargetTemperature=0
    CurrentSetpoint=0
    
    #check to which target to get
    if (Devices[PROGRAMSWITCH].nValue==30 and Devices[HOLIDAY].nValue==0) or Devices[DAYTIMEEXTENSION].nValue==1:
        CurrentSetpoint=float(Devices[DAYSETPOINT].sValue)
    elif Devices[PROGRAMSWITCH].nValue==10 or Devices[HOLIDAY].nValue==1:
        CurrentSetpoint=float(Devices[FROSTPROTECTIONSETPOINT].sValue)
    elif Devices[PROGRAMSWITCH].nValue==20: 
        CurrentSetpoint=float(Devices[NIGHTSETPOINT].sValue)
    else:
        Log("ERROR: Unable to get current setpoint")
        return False,None,None,None,None

   
    #Get Outside Temperature
    Succes,CurrentOutsideTemperature=GetTemperature(Parameters["Mode2"])
    if not Succes:
        Log("Failed to get outside temperature")
        return False,None,None,None,None 
   
    #Get Inside Temperature
    Succes,CurrentInsideTemperature=GetTemperature(Parameters["Mode3"])
    if not Succes:
        Log("Failed to get inside temperature")
        return False,None,None,None,None

    if Succes:
        #Check if we are in thermostat or Weather dependent mode
        if Devices[FPWD].nValue==0:
            Debug("Thermostat mode")
           
            Duration=time.time()-LastInsideTemperatureTimestamp
            if (CurrentOutsideTemperature<(Devices[SWITCHHEATINGOFFAT].nValue) or (CurrentInsideTemperature>(CurrentSetpoint+SwitchOffHeatingDelta))): #let's just switch off
                TargetTemperature =  GetPidValue(CurrentSetpoint, CurrentInsideTemperature, LastInsideTemperatureValue, Duration)
            else:
                Debug("Don't invoke PID, Outsidetemp is above minimum temp or too much above above setpoint")
                TargetTemperature=CurrentOutsideTemperature

            #remember current temp
            LastInsideTemperatureValue=CurrentInsideTemperature
            LastInsideTemperatureTimestamp=time.time()

            #Return Correct Values
            return True,TargetTemperature,CurrentOutsideTemperature,CurrentInsideTemperature,CurrentSetpoint
        else:
            Debug("Weather dependant mode")

            MaxYDelta=Devices[BOILERTEMPATMIN10].nValue-Devices[BOILERTEMPATPLUS20].nValue #boilertemp at -10 minus boilertemp at +20
            MaxXDelta=30 # 20 - (-10)=30

            #Calculate based on root function
            #Curvature=Devices[CURVATURESWITCH].nValue/20+1
            #MaxToReach=MaxYDelta**Curvature
            #TargetTemperature=((20-CurrentOutsideTemperature)/MaxXDelta*(MaxToReach))**(1/Curvature)+Devices[BOILERTEMPATPLUS20].nValue
            #Debug("Calculated temperature according to heating curve: "+str(TargetTemperature))

            #Calculation based on sine curve
            TargetTemperatureWithoutCurvature=(20-CurrentOutsideTemperature)/MaxXDelta*MaxYDelta+Devices[BOILERTEMPATPLUS20].nValue
            Curvature=math.sin(math.pi*(20-CurrentOutsideTemperature)/MaxXDelta)*Devices[CURVATURESWITCH].nValue*MaxYDelta/100
            TargetTemperature+=Curvature+TargetTemperatureWithoutCurvature
            #Debug("TargetTemperature = "+str(TargetTemperatureWithoutCurvature)+" + "+str(Curvature)+" = "+str(TargetTemperature))

            #Apply reference room compensation
            Succes,CurrentInsideTemperature=GetTemperature(Parameters["Mode3"])
            Compensation=Devices[REFERENCEROOMCOMPENSATION].nValue
            if Compensation>0:
                Debug("applying reference room temperature compensation: "+str((CurrentSetpoint-CurrentInsideTemperature)*Compensation))
                TargetTemperature+=(CurrentSetpoint-CurrentInsideTemperature)*Compensation
                
            # Make sure target temp remains within set boundaries
            if TargetTemperature>Devices[MAXBOILERTEMP].nValue:
                Debug("Calculated temp above max temp, correcting")
                TargetTemperature=Devices[MAXBOILERTEMP].nValue
            if TargetTemperature<Devices[MINBOILERTEMP].nValue:
                Debug("Calculated temp below min temp, correcting")
                TargetTemperature=Devices[MINBOILERTEMP].nValue

            #Return values
            return True,TargetTemperature,CurrentOutsideTemperature,CurrentInsideTemperature,CurrentSetpoint

def DomoticzAPI(APICall):
    resultJson = None
    url = "http://{}:{}/json.htm?{}".format(Parameters["Address"], Parameters["Port"], parse.quote(APICall, safe="&="))
    #Domoticz.Debug("Calling domoticz API: {}".format(url))
    try:
        req = request.Request(url)
        if Parameters["Username"] != "":
            #Domoticz.Debug("Add authentification for user {}".format(Parameters["Username"]))
            credentials = ('%s:%s' % (Parameters["Username"], Parameters["Password"]))
            encoded_credentials = base64.b64encode(credentials.encode('ascii'))
            req.add_header('Authorization', 'Basic %s' % encoded_credentials.decode("ascii"))

        response = request.urlopen(req)
        if response.status == 200:
            resultJson = json.loads(response.read().decode('utf-8'))
            if resultJson["status"] != "OK":
                Domoticz.Error("Domoticz API returned an error: status = {}".format(resultJson["status"]))
                resultJson = None
        else:
            Domoticz.Error("Domoticz API: http error = {}".format(response.status))
    except:
        Domoticz.Error("Error calling '{}'".format(url))
    return resultJson

def GetTemperature(TemperatureDeviceIDX):
    data = DomoticzAPI("type=devices&rid="+str(TemperatureDeviceIDX))
    try:
        CurrentTemperature=data["result"][0]["Temp"]
        return True,CurrentTemperature
    except:
        #Domoticz Error
        Log("error getting temperature from domoticz device with idx"+str(TemperatureDeviceIDX))
        return False,0

def GetPidValue(sp, pv, pv_last, dt):
    global ierr

    #Debug("sp="+str(sp)+", pv="+str(pv)+",pv_last="+str(pv_last)+",ierr="+str(ierr)+",dt="+str(dt))
    #sp=setpoint, pv=current temp, pv_last=last temp, dt=duration
    KP = 30
    KI = 0.02 #0.02 was org value
    KD = 10
    
    # upper and lower bounds on heater level
    ophi = Devices[MAXBOILERTEMP].nValue
    oplo = Devices[MINBOILERTEMP].nValue
    
    # calculate the error
    error = sp - pv;
    
    # calculate the integral error
    ierr = float(ierr) + float(KI) * float(error) * float(dt)
    
    # calculate the measurement derivative
    dpv = (pv - pv_last) / dt
    
    # calculate the PID output
    P = KP * error #proportional contribution
    I = ierr   #integral contribution  
    D = -KD*dpv #deritive contribution

    op = P + I + D
    
    #implement anti-reset windup
    #if ((op < oplo) or (op > ophi)):
     #   I = I - KI * error * dt
        #clip output
      #  op = max(oplo, min(ophi, op))

    if op<oplo:
        op=oplo
        if error<0:
            I = I - KI * error * dt

    if op>ophi:
        op=ophi
        if error>0:
            I = I - KI * error * dt
    
    ierr = I
    #Debug("sp=" + str(sp) + " pv=" + str(pv) + " dt=" + str(dt) + " op=" + str(op) + " P=" + str(P) + " I=" + str(I) + " D=" + str(D))
    Debug("Import;" + str(sp) + ";" + str(pv) + ";" + str(dt) + ";" + str(op) + ";" + str(P) + ";" + str(I) + ";" + str(D))
    return op

def CheckDebug():
    global Debugging
    
    #Check if we have to switch on debug mode
    if os.path.exists(str(Parameters["HomeFolder"])+"DEBUG"):
        Debugging=True
        Debug("File "+str(Parameters["HomeFolder"])+"DEBUG"+" exists, switched on Debug mode")
    else:
        Debug("File "+str(Parameters["HomeFolder"])+"DEBUG"+" does not exist, switching off Debug mode")
        Debugging=False #True/False



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
        global LastInsideTemperatureValue
        global LastInsideTemperatureTimestamp
        global ierr

        CheckDebug()  #Check if we have to enable debugging

        # Read config
        #for  x in Parameters:
        #    Debug("Paramater "+x+" is "+str(Parameters[x]))
        Hostname="http://"+Parameters["Mode1"]+"/" 

        DayTimeExtensionTime=int(Parameters["Mode4"])

        #Create parameter setpoints
        CreateParameters()

        #Update Devices
        getSensors()

        #Init Thermostat Values
        Succes,LastInsideTemperatureValue=GetTemperature(Parameters["Mode3"])
        LastInsideTemperatureTimestamp=time.time()
        Succes,CurrentOutsideTemperature=GetTemperature(Parameters["Mode2"])
        if Succes:
            ierr=LastInsideTemperatureValue  #Better starting point for ierr



    def onStop(self):
        Debug("onStop called")

    def onConnect(self, Connection, Status, Description):
        Debug("onConnect called")

    def onMessage(self, Connection, Data):
        Debug("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        global LastInsideTemperatureValue
        global LastInsideTemperatureTimestamp
        global ierr

        Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        #if Unit==in {CURVATURESWITCH or Unit==PROGRAMSWITCH:
        if Unit in {CURVATURESWITCH,MINBOILERTEMP,MAXBOILERTEMP,BOILERTEMPATMIN10,BOILERTEMPATPLUS20,SWITCHHEATINGOFFAT,
                DAYSETPOINT,NIGHTSETPOINT,FROSTPROTECTIONSETPOINT,REFERENCEROOMCOMPENSATION}:
            if float(Devices[Unit].sValue)!=float(Level):
                Devices[Unit].Update(nValue=int(Level), sValue=str(Level))
        elif Unit==PROGRAMSWITCH:
            Devices[Unit].Update(nValue=int(Level), sValue=str(Level))
            if Devices[Unit].nValue==0: 
                ESPCommand("command?BoilerTemperature=0&CentralHeating=off")
        elif Unit in {HOLIDAY,DAYTIMEEXTENSION,DHWCONTROL,FPWD}:
            #Handle Switch
            NewValue=0
            if Command=="On":
                NewValue=1
            Devices[Unit].Update(nValue=NewValue, sValue=Command)

            #If FirePlace/WeatherDependent switch was set: reset thermostat vars
            if (Unit==FPWD and Command=="Off"):
                #Reset Thermostat Values
                Succes,LastInsideTemperatureValue=GetTemperature(Parameters["Mode3"])
                LastInsideTemperatureTimestamp=time.time()
                Succes,CurrentOutsideTemperature=GetTemperature(Parameters["Mode2"])
                if Succes:
                    ierr=LastInsideTemperatureValue  #Better starting point for ierr
        elif Unit==ENABLECENTRALHEATING:
            if Command.lower()=="on":
                ESPCommand("command?CentralHeating=on")
            else:
                ESPCommand("command?CentralHeating=off")
        elif Unit==ENABLEHOTWATER:
            if Command.lower()=="on":
                ESPCommand("command?HotWater=on")
            else:
                ESPCommand("command?HotWater=off")
        elif Unit==ENABLECOOLING:
            if Command.lower()=="on":
                ESPCommand("command?Cooling=on")
            else:
                ESPCommand("command?Cooling=off")
        elif Unit==BOILERSETPOINT:
            ESPCommand("command?BoilerTemperature="+str(Level))
        elif Unit==DHWSETPOINT:
            ESPCommand("command?DHWTemperature="+str(Level))
        else: 
            Log("Unhandled command")

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Debug("onDisconnect called")

    def onHeartbeat(self):
        CheckDebug() #Check if we have to enable debug logging
        Debug("Number of seconds: "+str(int(time.time())% 60))

        if Devices[PROGRAMSWITCH].nValue==0:
            #Program inactive, just get sensors
            Debug("Program inactive")
            getSensors()
        else:
            Succes,TargetTemperature,CurrentOutsideTemperature,CurrentInsideTemperature,CurrentSetpoint=CalculateBoilerSetPoint()
            if Succes:
                Debug("Current Setpoint is "+str(CurrentSetpoint))
                #Program Active, try to get outside temperature
                if CurrentOutsideTemperature>(Devices[SWITCHHEATINGOFFAT].nValue):
                    Debug("outside temp aboven day treshold, leave or switch off heating")
                    #We are at the temperature at which we can switchoff heating
                    ESPCommand("command?CentralHeating=off&BoilerTemperature=0")
                else:
                    if (Devices[PROGRAMSWITCH].nValue==30 and Devices[HOLIDAY].nValue==0) or Devices[DAYTIMEEXTENSION].nValue==1:
                        #check if we have to deactivate extension
                        if Devices[DAYTIMEEXTENSION].nValue==1:
                            Debug("Day time extension active ["+Devices[DAYTIMEEXTENSION].LastUpdate+"]")
                            res = datetime.datetime(*(time.strptime(Devices[DAYTIMEEXTENSION].LastUpdate, "%Y-%m-%d %H:%M:%S")[0:6]))
                            delta=(datetime.datetime.now()-res).total_seconds()
                            Debug("Daytime extension was set"+str(int(delta)/60)+"minutes ago,"+str(int(DayTimeExtensionTime*60-delta))+" to switch back program again")
                            if (delta>DayTimeExtensionTime*60):
                                Log("DaytimeExtension expired, going back to normal program")
                                UpdateOnOffSensor("DayTime Extension",DAYTIMEEXTENSION,"Off")
                        Debug("Handling Day program")
                        #Manage Heating
                        if CurrentInsideTemperature>Devices[DAYSETPOINT].nValue+SwitchOffHeatingDelta:
                            Debug("Inside temp too much above setpoint, switching or leaving off heating")
                            ESPCommand("command?CentralHeating=off&BoilerTemperature=0")
                        else:
                            Debug("Setting boiler temp to "+str(TargetTemperature))
                            ESPCommand("command?CentralHeating=on&BoilerTemperature="+str(TargetTemperature))
                        #Manage DHW
                        if Devices[DHWCONTROL].nValue==1:
                            if  Devices[ENABLEHOTWATER].nValue==0:
                                Log("Switching on DHW")
                                ESPCommand("command?HotWater=on")

                    elif Devices[PROGRAMSWITCH].nValue==10 or Devices[HOLIDAY].nValue==1:
                        if Devices[HOLIDAY].nValue==1:
                            Debug("Holiday program active")
                        Debug("Handling Frost protection program")
                        #Manage DHW
                        if Devices[DHWCONTROL].nValue==1:
                            if  Devices[ENABLEHOTWATER].nValue==1:
                                Log("Switching off DHW")
                                ESPCommand("command?HotWater=off")
                        #Manage Heating
                        if Devices[FPWD].nValue==1:
                            Debug("Weather Dependent Mode")
                            if CurrentInsideTemperature<Devices[FROSTPROTECTIONSETPOINT].nValue:
                                #temperature too low, make there is heating
                                ESPCommand("command?CentralHeating=on&BoilerTemperature="+str(TargetTemperature))
                            else:
                                #temperature above setpoint, switch off heating
                                ESPCommand("command?CentralHeating=off&BoilerTemperature=0")
                        else:
                            Debug("Thermostat mode")
                            #Manage Heating
                            if CurrentInsideTemperature>Devices[FROSTPROTECTIONSETPOINT].nValue+SwitchOffHeatingDelta:
                                Debug("Inside temp too much above setpoint, switching or leaving off heating")
                                ESPCommand("command?CentralHeating=off&BoilerTemperature=0")
                            else:
                                Debug("Setting boiler temp to "+str(TargetTemperature))
                                ESPCommand("command?CentralHeating=on&BoilerTemperature="+str(TargetTemperature))

                    elif Devices[PROGRAMSWITCH].nValue==20:
                        Debug("Handling Night Program")
                        #Manage DHW
                        if Devices[DHWCONTROL].nValue==1:
                            if  Devices[ENABLEHOTWATER].nValue==1:
                                Log("Switching off DHW")
                                ESPCommand("command?HotWater=off")
                        #Manage Heating
                        if Devices[FPWD].nValue==1:
                            Debug("Weather Dependent Mode")
                            if CurrentInsideTemperature<Devices[NIGHTSETPOINT].nValue:
                                #temperature too low, make there is heating
                                #Check if we have to enable the central heating
                                ESPCommand("command?CentralHeating=on&BoilerTemperature="+str(TargetTemperature))
                            else:
                                ESPCommand("command?CentralHeating=off&BoilerTemperature=0")
                        else:
                            Debug("Thermostat mode")
                            #Manage Heating
                            if CurrentInsideTemperature>Devices[NIGHTSETPOINT].nValue+SwitchOffHeatingDelta:
                                Debug("Inside temp too much above setpoint, switching or leaving off heating")
                                ESPCommand("command?CentralHeating=off&BoilerTemperature=0")
                            else:
                                Debug("Setting boiler temp to "+str(TargetTemperature))
                                ESPCommand("command?CentralHeating=on&BoilerTemperature="+str(TargetTemperature))
                        
                    else:
                        Log("Unknow value of program switch: "+str(Devices[PROGRAMSWITCH].nValue))
            else:
                Log("No temperatures returned from calculateboilersetpoint, could not execute program")

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
