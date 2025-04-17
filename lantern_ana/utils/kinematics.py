from math import sqrt

def KE_from_fourmom( px, py, pz, E ):
    m2 = max(0.0,E*E - (px*px+py*py+pz*pz))
    m = sqrt(m2)
    ke = E-m
    return ke