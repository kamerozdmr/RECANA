import pandas as pd
import numpy as np
from scipy.interpolate import interp1d


def rounder(sayi):
    # Parametrelerde verilen enlem boylam değerlerine göre yuvarla
    r = round(sayi, 1) 
    if round((sayi - r),5) == 0.05 or round((sayi - r),5) == -0.05:
        a, b = round(sayi,4), round(sayi,4)
    else:
        a, b = round((r-0.05),4), round((r+0.05),4)
    return a, b

# https://github.com/gtuinsaat/TBDY2018_tepki_spektrumu
def CalculateSds(Ss, zemin):
    Ss_range = [0.25 , 0.50 , 0.75, 1.00 , 1.25 , 1.50 ]
    FS_table = {"ZA": [0.8 , 0.8 , 0.8 , 0.8 , 0.8 , 0.8], 
                "ZB": [0.9 , 0.9 , 0.9 , 0.9 , 0.9 , 0.9], 
                "ZC": [1.3 , 1.3 , 1.2 , 1.2 , 1.2 , 1.2],
                "ZD": [1.6 , 1.4 , 1.2 , 1.1 , 1.0 , 1.0],
                "ZE": [2.4 , 1.7 , 1.3 , 1.1 , 0.9 , 0.8]}
    
    # Kısa periyod hesabı
    if Ss < Ss_range[0]:
        FS_satir = np.polyfit(Ss_range[0:2], list(FS_table[zemin])[0:2], 1)
        FS_katsayisi = np.poly1d( FS_satir )
        Fs = float( format(FS_katsayisi(Ss) , '.2f') )
        Sds = Ss * Fs
    elif Ss > Ss_range[-1]:
        FS_satir = np.polyfit(Ss_range[-3:-1], list(FS_table[zemin])[-3:-1], 1)
        FS_katsayisi = np.poly1d( FS_satir )
        Fs = float( format(FS_katsayisi(Ss) , '.2f') )
        Sds = Ss * Fs    
    else:
        FS_satir = interp1d(Ss_range, FS_table[zemin], kind='linear')
        FS_katsayisi = FS_satir(Ss)
        Fs = round( float(FS_katsayisi) , 2) 
        Sds = Ss * Fs

    return Sds

def CalculateSd1(S1, zemin):
    S1_range = [0.10 , 0.20 , 0.30, 0.40 , 0.50 , 0.60 ]
    F1_table = {"ZA": [0.8 , 0.8 , 0.8 , 0.8 , 0.8 , 0.8], 
                "ZB": [0.8 , 0.8 , 0.8 , 0.8 , 0.8 , 0.8], 
                "ZC": [1.5 , 1.5 , 1.5 , 1.5 , 1.5 , 1.4],
                "ZD": [2.4 , 2.2 , 2.0 , 1.9 , 1.8 , 1.7],
                "ZE": [4.2 , 3.3 , 2.8 , 2.4 , 2.2 , 2.0]}
    
    # 1sn periyod hesabı
    if S1 < S1_range[0] :
        F1_satir = np.polyfit(S1_range[0:2], list(F1_table[zemin])[0:2], 1)
        F1_katsayisi = np.poly1d( F1_satir )
        F1 = float( format(F1_katsayisi(S1) , '.2f') )
        Sd1 = S1 * F1
    elif S1 > S1_range[-1]:
        F1_satir = np.polyfit(S1_range[-3:-1], list(F1_table[zemin])[-3:-1], 1)
        F1_katsayisi = np.poly1d( F1_satir )
        F1 = float( format(F1_katsayisi(S1) , '.2f') )
        Sd1 = S1 * F1

    else:    
        F1_satir = interp1d(S1_range, F1_table[zemin], kind='linear')
        F1_katsayisi = F1_satir(S1)
        F1 = round(float(F1_katsayisi) , 2)
        Sd1 = S1 * F1

    return Sd1

def CalculatEz(boylam, enlem, A, B, C, D):
    E= [boylam, enlem]
    #A-B  Enlem
    AB_E = (abs(E[1]-B[1])*A[2]*10) + (abs(E[1]-A[1])*B[2]*10)
    #C-D Enlem
    CD_E = (abs(E[1]-D[1])*C[2]*10) + (abs(E[1]-C[1])*D[2]*10)
    #AB_E-CD_E boylam
    Ez = (abs(E[0]-C[0])*AB_E*10) + (abs(E[0]-A[0])*CD_E*10)
    
    return Ez

def Vs30toSoiltype(vs30):
    if vs30 == 0:
        # if station has no vs30 value set use this vs30 value as default
        vs30 = 500  # ZC as default

    if vs30 > 1500:
        zemin = "ZA"
    elif 760 < vs30 <= 1500:
        zemin = "ZB"
    elif 360 < vs30 <= 760:
        zemin = "ZC"
    elif 180 < vs30 <= 360:
        zemin = "ZD"
    elif vs30 <= 180:
        zemin = "ZE"

    return zemin


def getAccCoeff(enlem, boylam, zemin, dd):
    # returns Sds and Sd1 coefficents
    
    ss_str = f"ss-{dd}"
    s1_str = f"s1-{dd}"

    df = pd.read_excel("files/tdth_parameters.xlsx")

    b_low, b_high = rounder(boylam)
    e_low, e_high = rounder(enlem) 
    
    # Boylam değerlerinin indexleri
    b_low_ind = df[df["boylam"]==b_low].index
    b_high_ind = df[df["boylam"]==b_high].index
    # Boylam değerleri dataframeler
    b_low_df = df.iloc[b_low_ind[0]:b_low_ind[-1]]
    b_high_df = df.iloc[b_high_ind[0]:b_high_ind[-1]]
    # Enlem değeri indexi
    bl_el_ind = b_low_df[b_low_df["enlem"]==e_low].index
    bl_eh_ind = b_low_df[b_low_df["enlem"]==e_high].index
    bh_el_ind = b_high_df[b_high_df["enlem"]==e_low].index
    bh_eh_ind = b_high_df[b_high_df["enlem"]==e_high].index
    
    soiltype = Vs30toSoiltype(zemin)
    if len(bl_el_ind)!= 0 or len(bl_eh_ind)!= 0 or len(bh_el_ind)!= 0 or len(bh_eh_ind)!= 0:
        # Koordinatlara ait ss değeri
        bl_el_ss = float(df.iloc[bl_el_ind][ss_str])       # A noktası     0,      0
        bl_eh_ss = float(df.iloc[bl_eh_ind][ss_str])       # B noktası     0,      0.05
        bh_el_ss = float(df.iloc[bh_el_ind][ss_str])       # C noktası     0.05,   0
        bh_eh_ss = float(df.iloc[bh_eh_ind][ss_str])       # D noktası     0.05,   0.05
        
        a_ss = [b_low, e_low, bl_el_ss] 
        b_ss = [b_low, e_high, bl_eh_ss]
        c_ss = [b_high, e_low, bh_el_ss]
        d_ss = [b_high, e_high, bh_eh_ss]

        Ss = CalculatEz(boylam, enlem, a_ss, b_ss, c_ss, d_ss)
        Sds = CalculateSds(Ss, soiltype)

        # Koordinatlara ait s1 değeri
        bl_el_s1 = float(df.iloc[bl_el_ind][s1_str])       # A noktası     0,      0
        bl_eh_s1 = float(df.iloc[bl_eh_ind][s1_str])       # B noktası     0,      0.05
        bh_el_s1 = float(df.iloc[bh_el_ind][s1_str])       # C noktası     0.05,   0
        bh_eh_s1 = float(df.iloc[bh_eh_ind][s1_str])       # D noktası     0.05,   0.05
        
        a_s1 = [b_low, e_low, bl_el_s1] 
        b_s1 = [b_low, e_high, bl_eh_s1]
        c_s1 = [b_high, e_low, bh_el_s1]
        d_s1 = [b_high, e_high, bh_eh_s1]

        S1 = CalculatEz(boylam, enlem, a_s1, b_s1, c_s1, d_s1)
        Sd1 = CalculateSd1(S1, soiltype)

        #round(Ss, 2), round(Sds, 2), round(S1, 2), round(Sd1, 2)
        return round(Sds, 2), round(Sd1, 2), soiltype




