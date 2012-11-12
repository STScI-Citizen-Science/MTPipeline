'''
The coordinate object is copied directly from the position.py submodule
of the astrolib.coords.

XXX
'''

import numpy as N

#-----------------------------------------------------------------------------
#Coordinate object

class Coord:
    """
    General class for subclasses.

    A Coord is distinct from a Position by being intrinsically expressed in
    a particular set of units.

    Each Coord subclass knows how to parse its own input, and convert itself
    into the internal representation (decimal degrees) used by the package.
    
    """

class Degrees(Coord):
    """
    Decimal degrees coord.

    Attributes
    ----------
    a1, a2 : float
        Longitude and latitude in decimal degrees.

    """

    def __init__(self,input):
        """
        Parameters
        ----------
        input : (float, float)
            Coordinates in decimal degrees.

        """
        self.a1,self.a2=input
        #Check for valid range
        #TPM supports -180<longitude<180
        #More usual convention is 0<longitude<360
        #Support both this way
        if not -180 <= self.a1 <= 360:
            raise ValueError, "Longitude %f out of range [-180,360]"%self.a1
        if not -90 <= self.a2 <= 90:
            raise ValueError, "Latitude %f out of range [-90,90]"%self.a2

    def __repr__(self):
        """
        Returns
        -------
        string

        """
        return "%f %f"%(self.a1,self.a2)

    def _calcinternal(self):
        return self.a1,self.a2

    def _calcradians(self):
        a1=(math.pi/180.0)*self.a1
        a2=(math.pi/180.0)*self.a2
        return a1,a2

class Radians(Coord):
    """
    Radians coord.

    Attributes
    ----------
    a1, a2 : float
        Longitude and latitude in radians.

    """
    
    def __init__(self,input):
        """
        Parameters
        ----------
        input : (float, float)
            Coordinates in radians.

        """
        self.a1, self.a2=input
        if not -1*math.pi <= self.a1 <=2*math.pi:
            raise ValueError, "Longitude %f out of range [0,2pi]"%self.a1
        if not -1*math.pi <= self.a2 <=math.pi:
            raise ValueError, "Latitude %f out of range [0,2pi]"%self.a2

    def __repr__(self):
        """
        Returns
        -------
        string

        """
        return "%f %f"%(self.a1,self.a2)

    def _calcinternal(self):
        """
        Convert radians to decimal degrees.

        Returns
        -------
        a1, a2 : (float, float)
            Decimal degrees.

        """
        a1=self.a1*(180.0/math.pi)
        a2=self.a2*(180.0/math.pi)
        return a1,a2

class Hmsdms(Coord):
    """
    Sexagesimal coord: longitude in hours of time (enforced).

    Attributes
    ----------
    a1, a2 : Numpy[int,int,float]
        Longitude and latitude in hours, minutes, seconds

    """

    def __init__(self,input):
        """
        Parameters
        ----------
        input : string
            Coordinates as hh:mm:ss.sss +dd:mm:ss.sss (sign optional).

        """
        #First break into two on spaces
        a1,a2=input.split()
        #Then break each one into pieces on colons
        hh,mm,ss=a1.split(':')
        #Check range
        if not 0 <= int(hh) <= 24:
            raise ValueError, "Hours %s out of range [0,24]"%hh
        if not 0 <= int(mm) <= 60:
            raise ValueError, "Minutes %s out of range [0,60]"%mm
        if not 0 <= float(ss) <= 60:
            raise ValueError, "Seconds %s out of range [0,60]"%ss
        self.a1=N.array([int(float(hh)),int(float(mm)),float(ss)])

        dd,mm,ss=a2.split(':')
        if not -90 <= int(dd) <= 90:
            raise ValueError, "Degrees %s out of range [-90,90]"%dd
        if not 0 <= int(mm) <= 60:
            raise ValueError, "Minutes %s out of range [0,60]"%mm
        if not 0 <= float(ss) <= 60:
            raise ValueError, "Seconds %s out of range [0,60]"%ss

        self.a2=N.array([int(float(dd)),int(float(mm)),float(ss)])

        #Check & fix for negativity
        if a2.startswith('-'):
            self.a2sign = '-'
            self.a2*= -1
        else:
            self.a2sign = '+'


    def __repr__(self):
        """
        Returns
        -------
        string

        """
        return "%dh %dm %5.3fs %s%dd %dm %5.3fs"%(self.a1[0],self.a1[1],self.a1[2],self.a2sign,abs(self.a2[0]),abs(self.a2[1]),abs(self.a2[2]))

    def _calcinternal(self):
        """
        Convert hmsdms to decimal degrees.

        Returns
        -------
        a1, a2 : (float, float)
            Decimal degrees.

        """
        a1= 15*self.a1[0] +   15*self.a1[1]/60.  +  15*self.a1[2]/3600.
        a2=abs(self.a2[0]) + abs(self.a2[1])/60. + abs(self.a2[2])/3600.
        if self.a2sign == '-':
            a2 = a2*(-1)
        return a1,a2