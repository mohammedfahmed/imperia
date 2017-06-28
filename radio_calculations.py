import numpy as np
import scipy.constants


def freespace_pathloss(p):
    return 20*np.log10(np.pi*4*p['distanceM']*p['frequencyHz']/scipy.constants.c)

def noisefloor_emane(p):
    return p['systemnoisefloordB'] + 10*np.log10(p['bandwidthHz']) - 174

def SINRdB(p):
    noiseFloordB = noisefloor_emane(p)
    rxpowerdB = p['txpowerdB'] + p['txgaindB'] + p['rxgaindB'] - freespace_pathloss(p)
    SINRdB = rxpowerdB - noiseFloordB
    return SINRdB

