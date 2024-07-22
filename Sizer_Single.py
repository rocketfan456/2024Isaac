# -*- coding: utf-8 -*-
"""

"""
import numpy as np
import matplotlib.pyplot as plt
import Classes_HW6 as cf

##############################################
# The actual running portion of the code
#
#
##############################################     


# Run through sequence
rocketData  = np.genfromtxt('C:/Users/isaac/Downloads/RocketData.csv', delimiter=',', dtype='f8') # load in the data file
nDataPointsMass = 1
# Pick your desired launch mass
mLaunched = [5250]


# Replace the values below with the data from the slides
ispSweep    = np.array([330])
thrEngine   = np.array([22240])
mrEngine    = np.array([2.3])
flgPressure     = np.array([1])   # 10 if the engine is pressure fed, 1 if the engine is pump fed
strOxEngine = ["Oxygen"]
strFuelEngine = ["RP-1"]
strEngType  = ["NotCryo"]
flgNew      = np.array([0]) # 0 if the engine exists, 1 if it doesn't
strEngName  = ["Leprechaun"]  # used for legend



# Rocket Information. Index to use and the cost of the rocket
rocketIndex = 2
cstRocket   = 85e6
fairingDiameter = 5


# Number of Prop Tanks and Radius
nTanks = 1
rMax = (fairingDiameter-0.2-0.024-0.15-0.3)/nTanks/2

# Target Payload
landerSize  = "Small"
goalPayload = 50
goalPower   = 400


strTankMat = "Stainless"


mStart      = np.zeros((nDataPointsMass, ispSweep.size))
mPayload    = np.zeros((nDataPointsMass, ispSweep.size))
mDry        = np.zeros((nDataPointsMass, ispSweep.size))
dv          = np.zeros((nDataPointsMass, ispSweep.size))
twPhase     = np.zeros((nDataPointsMass, ispSweep.size))
cost     = np.zeros((nDataPointsMass, ispSweep.size))


mdotRCS     = 3 / 86400     # divide by seconds per day to get rate per second




for jj,ispEngine in enumerate(ispSweep):   
    # The fifth column of rocketData (index 4) contains the rocket of interest
    mSeparated = mLaunched  
    for ii,mLaunch in enumerate(mSeparated):
        
        # Interpolate the data from the datafile
        apogeeOrbit = np.interp(mLaunch,rocketData[::-1,rocketIndex],rocketData[::-1,0]) # the weird -1 reverses the order of the data since interp expects increasing values
        
               
        
        dvReq   = cf.ApogeeRaise(apogeeOrbit)
        engMain = cf.Engine(ispEngine, thrEngine[jj], mrEngine[jj], 'Biprop', strEngType)
        
        
        engRCS  = cf.Engine(220, 448, 1, 'Monoprop', 'NotCryo')
        
        if engMain.strCryo == ['Cryo']:
            # Include chill-in and boiloff only for cryogenic sequence
            mdotOxBoiloff = 5/86400    # divide by seconds per day to get rate per second
            mdotFuelBoiloff = 10/86400  # divide by seconds per day to get rate per second 
            
            PreTLISett  = cf.Phase('Pre-TCM1 Settling',        mLaunch,       0, engMain,'Settling',      0, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            PreTLIChill = cf.Phase('Pre-TCM1 Chill',   PreTLISett.mEnd,       0, engMain, 'Chill',        0, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            TLI         = cf.Phase('TLI',             PreTLIChill.mEnd,   dvReq, engMain,  'Burn',        0, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            CoastToTCM1 = cf.Phase('Coast to TCM1',           TLI.mEnd,       0, engMain, 'Coast', 1*86400, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            PreTCM1Sett = cf.Phase('Pre-TCM1 Settling',CoastToTCM1.mEnd,      0, engMain,'Settling',      0, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            PreTCM1Chill= cf.Phase('Pre-TCM1 Chill',  PreTCM1Sett.mEnd,       0, engMain, 'Chill',       0, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            TCM1        = cf.Phase('TCM1',           PreTCM1Chill.mEnd,      20, engMain,  'Burn',        0, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            CoastToTCM2 = cf.Phase('Coast to TCM2',          TCM1.mEnd,       0, engMain, 'Coast', 2*86400, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            TCM2        = cf.Phase('TCM2',            CoastToTCM2.mEnd,       5,  engRCS,  'Burn',       0, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff) 
            CoastToTCM3 = cf.Phase('Coast to TCM3',          TCM2.mEnd,       0, engMain, 'Coast', 1*86400, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            TCM3        = cf.Phase('TCM3',            CoastToTCM3.mEnd,       5,  engRCS,  'Burn',        0, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            CoastToLOI  = cf.Phase('Coast to LOI',           TCM3.mEnd,       0, engMain, 'Coast', 0.5*86400, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            PreLOISett  = cf.Phase('Pre-LOI Settling', CoastToLOI.mEnd,       0, engMain,'Settling',      0, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            PreLOIChill = cf.Phase('Pre-LOI Chill',    PreLOISett.mEnd,       0, engMain, 'Chill',       0, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff) 
            LOI         = cf.Phase('LOI',             PreLOIChill.mEnd,     850, engMain,  'Burn',       0, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            CoastToTCM4 = cf.Phase('Coast to TCM4',           LOI.mEnd,       0, engMain, 'Coast', 0.5*86400, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            TCM4        = cf.Phase('TCM4',            CoastToTCM4.mEnd,       5, engRCS,  'Burn',        0, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            CoastToDOI  = cf.Phase('Coast to DOI',           TCM4.mEnd,       0, engMain, 'Coast', 0.5*86400, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            PreDOISett  = cf.Phase('Pre-DOI Settling', CoastToDOI.mEnd,       0, engMain,'Settling',      0, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            PreDOIChill = cf.Phase('Pre-DOI Chill',    PreDOISett.mEnd,       0, engMain, 'Chill',       0, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff) 
            DOI         = cf.Phase('DOI',             PreDOIChill.mEnd,      25, engMain, 'Burn',     0, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            CoastToPDI  = cf.Phase('Coast to PDI',            DOI.mEnd,       0, engMain, 'Coast', 0.5*86400, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            PrePDISett  = cf.Phase('Pre-PDI Settling', CoastToPDI.mEnd,       0, engMain,'Settling',      0, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            PrePDIChill = cf.Phase('Pre-PDI Chill',    PrePDISett.mEnd,       0, engMain, 'Chill',       0, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff) 
            PDI         = cf.Phase('PDI',             PrePDIChill.mEnd,      -1, engMain,  'Burn',       0, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
        
            Sequence = [PreTLISett, PreTLIChill, TLI, CoastToTCM1, PreTCM1Sett, PreTCM1Chill, TCM1,CoastToTCM2, TCM2, CoastToTCM3, \
            TCM3,CoastToLOI,PreLOISett, PreLOIChill, LOI, CoastToTCM4, TCM4,CoastToDOI, PreDOISett, PreDOIChill, DOI, CoastToPDI, \
                PrePDISett, PrePDIChill, PDI]
        
        else:
            # This is not a cryogenic engine, so we don't need chill-in or boiloff
            mdotOxBoiloff   = 0    # divide by seconds per day to get rate per second
            mdotFuelBoiloff = 0  # divide by seconds per day to get rate per second 
            
            PreTLISett  = cf.Phase('Pre-TCM1 Settling',        mLaunch,       0, engMain,'Settling',      0, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            TLI         = cf.Phase('TLI',              PreTLISett.mEnd,   dvReq, engMain,  'Burn',        0, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            CoastToTCM1 = cf.Phase('Coast to TCM1',           TLI.mEnd,       0, engMain, 'Coast', 1*86400, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            PreTCM1Sett = cf.Phase('Pre-TCM1 Settling',CoastToTCM1.mEnd,      0, engMain,'Settling',      0, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            TCM1        = cf.Phase('TCM1',           PreTCM1Sett.mEnd,      20, engMain,  'Burn',        0, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            CoastToTCM2 = cf.Phase('Coast to TCM2',          TCM1.mEnd,       0, engMain, 'Coast', 2*86400, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            TCM2        = cf.Phase('TCM2',            CoastToTCM2.mEnd,       5,  engRCS,  'Burn',       0, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff) 
            CoastToTCM3 = cf.Phase('Coast to TCM3',          TCM2.mEnd,       0, engMain, 'Coast', 1*86400, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            TCM3        = cf.Phase('TCM3',            CoastToTCM3.mEnd,       5,  engRCS,  'Burn',        0, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            CoastToLOI  = cf.Phase('Coast to LOI',           TCM3.mEnd,       0, engMain, 'Coast', 0.5*86400, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            PreLOISett  = cf.Phase('Pre-LOI Settling', CoastToLOI.mEnd,       0, engMain,'Settling',      0, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            LOI         = cf.Phase('LOI',              PreLOISett.mEnd,     850, engMain,  'Burn',       0, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            CoastToTCM4 = cf.Phase('Coast to TCM4',           LOI.mEnd,       0, engMain, 'Coast', 0.5*86400, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            TCM4        = cf.Phase('TCM4',            CoastToTCM4.mEnd,       5, engRCS,  'Burn',        0, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            CoastToDOI  = cf.Phase('Coast to DOI',           TCM4.mEnd,       0, engMain, 'Coast', 0.5*86400, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            PreDOISett  = cf.Phase('Pre-DOI Settling', CoastToDOI.mEnd,       0, engMain,'Settling',      0, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            DOI         = cf.Phase('DOI',             PreDOISett.mEnd,      25, engMain, 'Burn',     0, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            CoastToPDI  = cf.Phase('Coast to PDI',            DOI.mEnd,       0, engMain, 'Coast', 0.5*86400, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            PrePDISett  = cf.Phase('Pre-PDI Settling', CoastToPDI.mEnd,       0, engMain,'Settling',      0, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            PDI         = cf.Phase('PDI',              PrePDISett.mEnd,      -1, engMain,  'Burn',       0, mdotRCS, mdotOxBoiloff, mdotFuelBoiloff)
            
            Sequence = [PreTLISett, TLI, CoastToTCM1, PreTCM1Sett, TCM1,CoastToTCM2, TCM2, CoastToTCM3, \
            TCM3,CoastToLOI,PreLOISett,LOI,CoastToTCM4, TCM4,CoastToDOI, PreDOISett, DOI, CoastToPDI, \
                PrePDISett, PDI]
        
        # Create the Misison Summary and calculate subsystem masses with payload 
        Mission = cf.MissionSummary(Sequence)
        
        # Check tanks based on Isp (since each value is a different propellant

        OxTanks = cf.TankSet(strOxEngine[jj], strTankMat, nTanks, rMax, 300000*flgPressure[jj], Mission.mPropTotalOx)
        FuelTanks = cf.TankSet(strFuelEngine[jj], strTankMat, nTanks, rMax, 300000*flgPressure[jj], Mission.mPropTotalFuel)

        
        # Calculate monopropellant tank size
        MonoTanks = cf.TankSet("MMH", "Stainless", 1, 2, 300000, Mission.mPropTotalMono)    
        
        subs = cf.Subsystems(mLaunch, engMain, OxTanks, FuelTanks, MonoTanks, goalPower, 'Deployable', landerSize, 8)
        
        # Determine payload
        payload = mLaunch - Mission.mPropTotalTotal - subs.mTotalAllowable

        # Determine Cost
        costObject = cf.Cost(subs.mTotalAllowable,  thrEngine[jj]*flgNew[jj], cstRocket)
        cost[ii,jj] = costObject.costNRETotal
        
        # Save values for plotting        
        mStart[ii, jj] = mLaunch
        mPayload[ii, jj] = payload
        mDry[ii,jj] = subs.mTotalAllowable
        
        
        


cf.PrintPhasePropData(Sequence)
print(' ')
cf.PrintMassData(subs)
print(' ')
cf.PrintPropData(Mission)
print(' ')
print('{0:30s}{1:11.1f}'.format("Allowable Dry Mass", subs.mTotalAllowable))
print('{0:30s}{1:11.1f}'.format("Total Propellant", Mission.mPropTotalTotal))
print('{0:30s}{1:11.1f}'.format("Payload", payload))
print('{0:30s}{1:11.1f}'.format("Launch Mass", subs.mTotalAllowable+Mission.mPropTotalTotal+payload))
print(' ')
print('{0:30s}{1:11.1f}{2:30s}'.format("RE Lander Cost ", np.round((costObject.costRELander/1e6), decimals=2), " M$"))
print('{0:30s}{1:11.1f}{2:30s}'.format("NRE Lander Cost ", np.round((costObject.costNRELander/1e6), decimals=2), " M$"))
print('{0:30s}{1:11.1f}{2:30s}'.format("NRE Engine Cost ", np.round((costObject.costNREEngine/1e6), decimals=2), " M$"))
print('{0:30s}{1:11.1f}{2:30s}'.format("Total Cost ", np.round((costObject.costNRETotal/1e6), decimals=2), " M$"))
print(' ')




