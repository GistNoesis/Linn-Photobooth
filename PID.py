from collections import deque


class PIDController:
    def __init__(self,t0, Kp,Ki,Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.output = 0
        self.I = 0
        self.t =t0
        self.recentPoints = deque()




    def AppendPoint(self, currentTime, err):
        self.recentPoints.append( (currentTime,err))
        #remove oldPoints
        while( currentTime  - self.recentPoints[0][0] > 0.5 and len(self.recentPoints)>1 ):
            self.recentPoints.popleft()

        dt = currentTime - self.t
        if len(self.recentPoints) == 1:
            D = 0
        else:
            w = 1.0
            D = (1-w)*(err -  self.recentPoints[0][1] )/ ( currentTime - self.recentPoints[0][0]) + w*(err-self.recentPoints[-2][1]) / ( currentTime - self.recentPoints[-2][0])

        if( dt < 1.0):
            self.I += dt* err
        else:
            self.I = 0

        self.output = self.Kp*err + self.Ki* self.I + self.Kd*D
        self.t = currentTime