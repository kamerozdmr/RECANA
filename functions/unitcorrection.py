
def unitcorrection(unit):
    
    if unit == "g":
        unitcalibration = float(9.81)

    elif  unit == "mg":
        unitcalibration = float(0.00981)

    elif unit == "m/s/s":
        unitcalibration = float(1)

    elif unit == "cm/s/s" or unit == "gal":
        unitcalibration = float(0.01)

    else:
        raise Exception("Given unit is not recognized")

    return unitcalibration

def velocityunit(acc_unit):

    if acc_unit == "g":
        vel_unit = "m/s"
        vel_factor = float(1/9.81)

    elif acc_unit == "m/s/s":
        vel_unit = "m/s"
        vel_factor = float(1)

    elif acc_unit == "mg":
        vel_unit = "cm/s"
        vel_factor = float(10/9.81)

    elif acc_unit == "cm/s/s" or acc_unit == "gal":
        vel_unit = "cm/s"
        vel_factor = float(1)

    elif acc_unit == "Raw":
        vel_unit = "Raw"
        vel_factor = float(1)
    
    return vel_unit, vel_factor


def displacementunit(vel_unit):

    if vel_unit == "m/s":
        disp_unit = "m"
        disp_factor = float(1)

    elif vel_unit == "cm/s":
        disp_unit = "cm"
        disp_factor = float(1)

    elif vel_unit == "Raw":
        disp_unit = "Raw"
        disp_factor = float(1)

    return disp_unit, disp_factor

def spectrumunit(acc_unit):

    if acc_unit == "g":
        spec_unit = float(1)

    elif acc_unit == "m/s/s":
        spec_unit = float(9.81) 

    elif acc_unit == "mg":
        spec_unit = float(1000) 

    elif acc_unit == "gal" or acc_unit == "cm/s/s":
        spec_unit = float(981)

    acc_unit = "g"

    return spec_unit, acc_unit
    

def ariasunit(acc_unit):

    if acc_unit == "g":
        spec_unit = float(1/9.81)
        acc_unit = "m/s"

    elif acc_unit == "m/s/s":
        spec_unit = 1 
        acc_unit = "m/s"

    elif acc_unit == "mg":
        spec_unit = float(1000/9.81) 
        acc_unit = "m/s"

    elif acc_unit == "gal" or acc_unit == "cm/s/s":
        spec_unit = 100
        acc_unit = "m/s"

    elif acc_unit== "Raw":
        spec_unit = 1
        acc_unit = "Raw"

    return spec_unit, acc_unit


def scavunit(acc_unit):

    if acc_unit == "g":
        scav_factor = float(0.025)

    elif acc_unit == "m/s/s":
        scav_factor = float(0.025*9.81)

    elif acc_unit == "mg":
        scav_factor = float(0.025*1000)

    elif acc_unit == "cm/s/s" or acc_unit == "gal":
        scav_factor = float(0.025*9.81*100)

    return scav_factor


def responseunit(acc_unit):

    if acc_unit == "g":
        response_factor = float(1)

    elif acc_unit == "Raw":
        response_factor = float(1)

    elif acc_unit == "m/s/s":
        response_factor = float(9.81)

    elif acc_unit == "mg":
        response_factor = float(1000)

    elif acc_unit == "cm/s/s" or acc_unit == "gal":
        response_factor = float(981)

    return response_factor




