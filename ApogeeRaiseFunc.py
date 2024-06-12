import numpy as np

def ApogeeRaise(startingApogee):
    ## Velocity calc: v = np.sqrt(mu*((2/r)-(1/a)))

    # Calc starting velocity at original orbit
    mu = 398600 # km^2/s^2
    periapsis = 185 #km
    rEarth = 6378 # km
    rTotal = rEarth + periapsis # km
    a = ((startingApogee+rEarth)+rTotal)/2 # km
    startingV = np.sqrt(mu*((2/rTotal)-(1/a))) # m/s

    # Calculate the needed velocity for new Apogee of 410,000 km
    newApogee = 410000 # km (given)
    aNew = ((newApogee+rEarth)+rTotal)/2 # km
    newV = np.sqrt(mu*((2/rTotal)-(1/aNew))) # m/s

    dV = newV - startingV # km/s

    # Find the difference between the two, returning needed dV
    return dV*1000 # m/s


