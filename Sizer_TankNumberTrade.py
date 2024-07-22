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

# 
# Run through sequence
rocketData  = np.genfromtxt('C:/Users/isaac/Downloads/RocketData.csv', delimiter=',', dtype='f8') # load in the data file
nDataPointsMass = 20


# Replace the values below with the data from your chosen engine
namesEng = ["ND-1", "Leprechaun", "Rockne", "Sorin"]
ispEngine    = [305, 330, 350, 310] # ND-1, Leprechaun, Rockne, Sorin
mrEngine    = np.array([1.8, 2.3, 2.8, 1.8]) # NTO/MMH, LOX/RP-1, LOX/Methane, NTO/MMH
thrEngine   = np.array([2224, 22240, 35584, 8896])
flgPressure     = np.array([10, 1, 1, 10])   # 10 if the engine is pressure fed, 1 if the engine is pump fed
strOxEngine = ["NTO", "Oxygen", "Oxygen", "NTO"]
strFuelEngine = ["MMH", "RP-1", "Methane", "MMH"]
strEngType  = ["NotCryo", "NotCryo", "Cryo", "NotCryo"]
flgNew      = np.array([0, 0, 0, 0]) # 0 if the engine exists, 1 if it doesn't


# Tank material options
strTankMat = ["Al2219", "Stainless", "Al-Li"]

# Rocket Information. Index to use and the cost of the rocket
namesRocket = ["Scout", "Juno", "Vanguard", "Nike"]
rocketIndex = np.arange(1,5)
cstRocket   = [60e6, 85e6, 100e6, 150e6]
fairingDiameter = [3.8, 5, 5, 7]

# Number of Prop Tanks and Radius
nTanks = np.array([1,2,3])

# Target Payload
landerSize  = "Small"
goalPayload = 50
goalPower   = 400


mStart      = np.zeros((nDataPointsMass, nTanks.size))
mPayload    = np.zeros((nDataPointsMass, nTanks.size))
mDry        = np.zeros((nDataPointsMass, nTanks.size))
dv          = np.zeros((nDataPointsMass, nTanks.size))
twPhase     = np.zeros((nDataPointsMass, nTanks.size))
cost     = np.zeros((nDataPointsMass, nTanks.size))


mdotRCS     = 3 / 86400     # divide by seconds per day to get rate per second

for iRocket in range(np.size(rocketIndex)):
    countFigs = 0 # Count of the number of figures being saved

    for iEng in range(np.size(ispEngine)):
        for iTankMat in range(np.size(strTankMat)):
            for jj,numTanks in enumerate(nTanks):   
                rMax = (fairingDiameter[iRocket]-0.2-0.024-0.15-0.3)/numTanks/2

                # The fifth column of rocketData (index 4) contains the rocket of interest
                mSeparated  = np.linspace(rocketData[-1,rocketIndex[iRocket]], rocketData[0,rocketIndex[iRocket]], nDataPointsMass)
                for ii,mLaunch in enumerate(mSeparated):
                    
                    # Interpolate the data from the datafile
                    apogeeOrbit = np.interp(mLaunch,rocketData[::-1,rocketIndex[iRocket]],rocketData[::-1,0]) # the weird -1 reverses the order of the data since interp expects increasing values
                    
                        
                    
                    dvReq   = cf.ApogeeRaise(apogeeOrbit)
                    engMain = cf.Engine(ispEngine[iEng], thrEngine[iEng], mrEngine[iEng], 'Biprop', strEngType[iEng])
                    
                    
                    engRCS  = cf.Engine(220, 448, 1, 'Monoprop', 'NotCryo')
                    
                    
                    if engMain.strCryo == 'Cryo':
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

                    OxTanks = cf.TankSet(strOxEngine[iEng], strTankMat[iTankMat], numTanks, rMax, 300000*flgPressure[iEng], Mission.mPropTotalOx)
                    FuelTanks = cf.TankSet(strFuelEngine[iEng], strTankMat[iTankMat], numTanks, rMax, 300000*flgPressure[iEng], Mission.mPropTotalFuel)

                    
                    # Calculate monopropellant tank size
                    MonoTanks = cf.TankSet("MMH", "Al2219", 1, 2, 300000, Mission.mPropTotalMono)    
                    
                    subs = cf.Subsystems(mLaunch, engMain, OxTanks, FuelTanks, MonoTanks, goalPower, 'Deployable', landerSize, 8)
                    
                    # Determine payload
                    payload = mLaunch - Mission.mPropTotalTotal - subs.mTotalAllowable
                    
                    # Determine Cost
                    costObject = cf.Cost(subs.mTotalAllowable,  thrEngine[iEng]*flgNew[iEng], cstRocket[iRocket])
                    cost[ii,jj] = costObject.costNRETotal
                    
                    # Save values for plotting        
                    mStart[ii, jj] = mLaunch
                    mPayload[ii, jj] = payload
                    mDry[ii,jj] = subs.mTotalAllowable
            
            # Plot Results for each combination of engine tank material and rocket
            startVal = mSeparated[0]
            endVal = mSeparated[nDataPointsMass-1]
            legString = ["goalPayload"]
            fig1 = plt.figure()
            ax1 = fig1.add_subplot(2,1,1)
            ax1.plot([startVal, endVal], [goalPayload, goalPayload], color='k')
            for ii in range(nTanks.size):  
                legString.append(nTanks[ii])                 
                ax1.plot(mStart[:,ii], mPayload[:,ii], linewidth=3.0)
            ax1.legend((legString))
            ax1.set_title(namesEng[iEng] + "," + strTankMat[iTankMat] + "," + namesRocket[iRocket])
            ax1.grid()
            ax1.set_xlabel('Start Mass (kg)')
            ax1.set_ylabel('Payload (kg)')

            legString = []
            ax2 = fig1.add_subplot(2,1,2)
            for ii in range(nTanks.size):  
                legString.append(nTanks[ii])                 
                ax2.plot(mStart[:,ii], cost[:,ii]/1000000, linewidth=3.0) 
            ax2.grid()
            ax2.set_xlabel('Start Mass (kg)')
            ax2.set_ylabel('Cost ($M)')
            ax2.legend((legString))
            countFigs = countFigs + 1
            plt.subplots_adjust(hspace = 0.3)
            plt.savefig(namesRocket[iRocket]+str(countFigs)+".png")
            plt.close()



