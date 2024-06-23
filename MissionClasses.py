
import numpy as np


# This function will output a summary of each phase
def PrintData(phaseList):
    print('{0:25s}'.format("-----------------------------------------------------------------------------------------" ))
    print('{0:20s}{1:>11s}{2:>11s}{3:>11s}{4:>13s}{5:>13s}{6:>14s}'.format("Phase Name", "DV (m/s)", "Mass0 (kg)", "MassF (kg)", "TotProp (kg)", "OxProp (kg)", "FuelProp (kg)"  ))
    print('{0:25s}'.format("-----------------------------------------------------------------------------------------" ))
    for curPhase in phaseList:
        print('{0:20s}{1:11.1f}{2:11.1f}{3:11.1f}{4:13.1f}{5:13.1f}{6:14.1f}'.format(curPhase.strName, curPhase.dvPhase, curPhase.mStart, curPhase.mEnd, curPhase.mPropImpulse, curPhase.mPropImpulseOx, curPhase.mPropImpulseFuel ))

# This class will create a generic "phase" which will do propellant 
# calculations
class Phase:

    def __init__(self,strName, mStart, dvPhase, clsEng):

        # Check if this is a T/W phase. If so, 
        # update the dV calculate the thrust-to-weight
        twPhase = clsEng.thrust/(mStart*9.81)
        if dvPhase<0:
            dvPhase = 4335*np.exp(-twPhase*20.25)+1880 #use the thrust-to-weight equation from the slides

        # Calculate Impulse Propellant Using Rocket Equation   
        # We specify Impulse because we'll have other types later
        mPropImpulse = mStart-(mStart/(np.exp(dvPhase/(9.81*clsEng.isp))))
   
        # Determine Oxidizer and Fuel
        mPropImpulseOx = (mPropImpulse*clsEng.mr)/(1+clsEng.mr)
        mPropImpulseFuel = mPropImpulse/(1+clsEng.mr)
        
          
        mEnd = mStart - mPropImpulse 
        
        
        # Move data to class structure to save information
        self.mStart         = mStart
        self.mEnd           = mEnd
        self.dvPhase        = dvPhase
        self.clsEng         = clsEng
        self.strName        = strName
        self.twPhase        = twPhase

        self.mPropImpulse   = mPropImpulse
        self.mPropImpulseOx = mPropImpulseOx
        self.mPropImpulseFuel = mPropImpulseFuel
 
# This class creates a summary of the entire mission - summing things up across
# phases         
class MissionSummary:
    def __init__(self, tupPhases):
        """
        Inputs:
            tupPhases: list of phase classes
        
        """
        # Initialize variables 
        mPropImpulse     = 0
        mPropImpulseOx   = 0
        mPropImpulseFuel = 0

        # sum up the usages by phase
        for curPhase in tupPhases:
            mPropImpulse     += curPhase.mPropImpulse 
            mPropImpulseOx   += curPhase.mPropImpulseOx
            mPropImpulseFuel += curPhase.mPropImpulseFuel

        # Stuff everything into self    
        self.mPropImpulse      = mPropImpulse
        self.mPropImpulseOx    = mPropImpulseOx
        self.mPropImpulseFuel  = mPropImpulseFuel


# This builds up an engine, with an assumed thrust, specific impulse, and 
# mixture ratio
class Engine:
    def __init__(self,isp, thrust, mr):
        self.isp = isp
        self.thrust = thrust
        self.mr = mr

class TankSet:
    def __init__(self, strPropType,strMatType, nTanks, lMaxRadTank, presTank, mPropTotal):
        # General Parameters for Tanks
        pctUllage =  0.1        # Extra ullage room as a percentage of tank volume
        aMax      =  50         # Maximum acceleration (m/s2)
        pctFudge  =  1.2        # Fudge factor for welds, etc
        fosMat    =  1.5        # factor of safety for material (nd)
        
        # Tank material switch case
        if strMatType=="Al2219":
            rhoMat = 2840     # Density of material (kg/m3)
            sigMat = 2.9e8    # Yield Stress of material (Pa)
            thkMin = 0.004    # Minimum thickness of material (m)
        elif strMatType=="Stainless":
            rhoMat = 8000
            sigMat = 2.15e8
            thkMin = 0.0004
        elif strMatType == "Al-Li":
            rhoMat = 2700
            sigMat = 7e8
            thkMin = 0.004
    
        
        # Propellant Density switch case
        if strPropType=="Oxygen":
            rhoProp = 1140     # Density of propellant (kg/m3)
        elif strPropType=="Hydrogen":
            rhoProp = 70
        elif strPropType == "Methane":
            rhoProp = 420
        elif strPropType == "MMH":
            rhoProp = 866
        elif strPropType == "NTO":
            rhoProp = 1450
        elif strPropType == "RP-1":
            rhoProp = 820
        
        
        # Calculate propellant volume and volume per tank (include ullage)
        volPropTotal    = mPropTotal/rhoProp
        volPropPerTank  = volPropTotal/nTanks
        volPerTank      = volPropPerTank*(1+pctUllage)
        
        # Compare volume of tank to maximum allowable for given radius
        #    This will help us determine if the tank is a sphere or a pill.
        volMaxRadius    = 4/3*np.pi*(lMaxRadTank**3)
        
        if volMaxRadius>volPerTank:
            # A sphere with the max radius is too big, so calculate
            # the needed radius and set cylinder length to zero
            lRadiusTank = (volPerTank*3/4/np.pi)**(1/3)
            lCylTank   = 0
            
        else:
            # A sphere with the max radius is too small, so calculate
            # what the cylinder length will be
            lRadiusTank = lMaxRadTank
            lCylTank    = (volPerTank-4/3*np.pi*(lRadiusTank**3))/(np.pi*lRadiusTank**2)
       
        # Calculate the total length of the tank 
        lTankLength = 2*lRadiusTank + lCylTank
        
        # Calculate the surface area of each portion of the tank
        saDomesPerTank   = 4*np.pi*lRadiusTank**2
        saCylinderPerTank = 2*np.pi*lRadiusTank*lCylTank
        saTotalPerTank   = saDomesPerTank + saCylinderPerTank
       
        # Calculate the thickness.  Start with pressure
        presTotal = fosMat*(presTank + rhoProp*aMax*lTankLength)
        thkDomesCalc  = (presTotal*lRadiusTank)/(2*sigMat)
        thkCylCalc    = (presTotal*lRadiusTank)/(sigMat)
        
        # Compare the pressure thickness to the minimum thickness
        thkDomes  = max(thkDomesCalc,thkMin)
        thkCyl    = max(thkCylCalc,thkMin)

        # Calculate the volume of the material
        volMatDomesPerTank = thkDomes*saDomesPerTank
        volMatCylPerTank   = thkCyl*saCylinderPerTank
        
        # Calculate the mass of each tank
        mDomesPerTank = volMatDomesPerTank*rhoMat
        mCylPerTank   = volMatCylPerTank*rhoMat
        
        # Add in the fudge factor 
        mTotalPerTank = (mDomesPerTank + mCylPerTank)*pctFudge
        mTotal        = (mTotalPerTank*nTanks)*(1.1**nTanks)

        # Stuff everything back into "self" for output
        self.strPropType = strPropType
        self.strMatType  = strMatType
        self.nTanks      = nTanks
        self.lMaxRadTank = lMaxRadTank
        self.presTank    = presTank
        self.mPropTotal  = mPropTotal
       
        self.pctUllage       = pctUllage
        self.rhoProp         = rhoProp
        self.volPropTotal    = volPropTotal
        self.volPropPerTank  = volPropPerTank
        self.volPerTank      = volPerTank
        self.volMaxRadius    = volMaxRadius
        self.lRadiusTank     = lRadiusTank
        self.lCylTank        = lCylTank
        self.lTankLength     = lTankLength
        self.saDomesPerTank     = saDomesPerTank
        self.saCylinderPerTank  = saCylinderPerTank
        self.saTotalPerTank  = saTotalPerTank
        self.presTotal       = presTotal
        self.thkDomesCalc    = thkDomesCalc
        self.thkCylCalc      = thkCylCalc
        self.thkDomes        = thkDomes
        self.thkCyl          = thkCyl
        self.volMatDomesPerTank = volMatDomesPerTank
        self.volMatCylPerTank = volMatCylPerTank
        self.mDomesPerTank   = mDomesPerTank
        self.mCylPerTank     = mCylPerTank
        self.mTotalPerTank   = mTotalPerTank
        self.mTotal          = mTotal

class Subsystems:
    def __init__(self, mVehicleStart, clsEng, clsOxTankSet,clsFuelTankSet, pwrDrawPayload, strArrayType, strLanderSize, tBattery):
        pctMarginArray      = 0.30
        pctDepthOfDischarge = 0.30
        nrgdenBattery       = 100 # w-hr/kg
        rhoSOFI             = 50 # Foam insulation density (kg/m3)
        thkSOFI             = 0.005 # Foam insulation thickness (m)
        rhoMLI              = 80 # multi-layer insulation density (kg/m3)
        thkMLI              = 0.001 # multi-layer insulation thickness (m)
        pctLandingGear      = 0.08
        pctStructure        = 0.20
        pctMGA              = 0.15 # mass growth allowance
        pctMargin           = 0.15 # mass margin percentage
        
        # Avionics
        mAvionics =
        
        # Electrical Subsystem      
        if strLanderSize =='Small':
            mPowerConversion = 
            pwrDrawLander    =  # W
        else:
            mPowerConversion = 50
            pwrDrawLander    = 1200
        
        if strArrayType == 'Body':
            pwrdenArray =  # w/kg
        else: 
            pwrdenArray =  # w/kg
        
        lTank = max() # pick the maximum length of your clsOxTankSet.lTankLength and clsFuelTankSet.lTanklength
        mWiring   = 
        
        pwrTotalMargined = (1+pctMarginArray)*()#the parenthesis is the sum of lander power and payload power
        mSolarArray      = #divide the total margined power by the density 
        
        nrgTotal       = 
        nrgTotalMargin = 
        mBattery       = 
        
        mElectrical = mPowerConversion+mWiring + mSolarArray + mBattery
        
        # Propulsion
        if strLanderSize =='Small':
            mRCS = 
            mPressurization = 
            mFeedlines = 
        else:
            mRCS = 
            mPressurization = 
            mFeedlines = 
            
        if clsOxTankSet.strPropType == 'Oxygen':
            mSOFIOx = 
            mMLIOx  = 
        else:
            mSOFIOx = 0
            mMLIOx  = thkMLI*clsOxTankSet.saTotalPerTank*clsOxTankSet.nTanks*rhoMLI

        if clsFuelTankSet.strPropType == 'Hydrogen':
            mSOFIFuel = thkSOFI*clsFuelTankSet.saTotalPerTank*clsFuelTankSet.nTanks*rhoSOFI
            mMLIFuel  = thkMLI*clsFuelTankSet.saTotalPerTank*clsFuelTankSet.nTanks*rhoMLI
            twEngine  = 
        elif clsFuelTankSet.strPropType == 'Methane':
            mSOFIFuel = 
            mMLIFuel  = 
            twEngine = 
        elif clsFuelTankSet.strPropType == 'MMH':
            mSOFIFuel = 
            mMLIFuel  = 
            twEngine = 
        elif clsFuelTankSet.strPropType == 'RP-1':
            mSOFIFuel = 0
            mMLIFuel  = 
            twEngine  = 
        
        mEngine = 1/(twEngine/clsEng.thrust)/9.81

        mPropulsion = 

        # Thermal
        mThermal = 
        
        # Structure
        mDryWithoutStructure = mAvionics + mElectrical + mPropulsion + mThermal 
        mStructureAndGear    = mDryWithoutStructure/(1-(pctStructure+pctLandingGear) )*(pctStructure+pctLandingGear)
        
        mTotalBasic     = mDryWithoutStructure + mStructureAndGear
        mMGA            = 
        mTotalPredicted = 
        mMargin         = 
        mTotalAllowable = 
        
            
        self.mAvionics         = 
        self.mWiring           = 
        self.pwrTotalMargined  = 
        self.mSolarArray       = 
        self.nrgTotal          = 
        self.nrgTotalMargin    = 
        self.mBattery          = 
        self.mElectrical       = 
        self.mSOFIOx           = 
        self.mSOFIFuel         = 
        self.mMLIOx            = 
        self.mMLIFuel          = 
        self.twEngine          = 
        self.mEngine           = 
        self.mPropulsion       = 
        self.mThermal          = 
        self.mDryWithoutStructure = 
        self.mStructureAndGear = 
        self.mTotalBasic       = 
        self.mMGA              = 
        self.mMargin           = 
        self.mTotalPredicted   = 
        self.mTotalAllowable   = 