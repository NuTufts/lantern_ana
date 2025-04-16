from math import sqrt

def KE_from_fourmom( px, py, pz, E ):
    m = sqrt( E*E - px*px+py*py+pz*pz )
    ke = E-m
    return ke