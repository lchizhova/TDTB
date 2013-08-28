import numpy as np
import matplotlib.pylab as plt
import math

#light_speed = 3 * 10**(8)

class VectorPotential:
    
    def __init__(self):
        self.frequency = None
        self.amplitude = None
        self.pulse_duration = None
    
    def __envelope(self, t):
        pass

    def get_electric_field(self, t):
        dt = 0.01 * 10**(-16)
        return [-(self(t + dt)[0] - self(1.*t)[0]) / dt, -(self(t + dt)[1] - self(1.*t)[1]) / dt]
    
    def get_magnetic_filed(self):
        pass
    
    def plot_electric_field(self, **kwrds):
        tarr = np.linspace(-0.1 / self.frequency, 7 * np.pi / self.frequency, 100)
        plt.subplot(1,2,1)
        Ex = [self.get_electric_field(t)[0] for t in tarr]
        plt.plot(tarr, Ex, label = r'$E_x$', **kwrds)
        plt.subplot(1,2,2)
        Ey = [self.get_electric_field(t)[1] for t in tarr]
        plt.plot(tarr, Ey, label = r'$E_y$', **kwrds)
    
    def plot_vector_potential(self, trange=None, **kwrds):
        if trange is None:
            tarr = np.linspace(-0.1 / self.frequency, 7 * np.pi / self.frequency, 100)
        else:
            tarr = trange
        plt.subplot(1,2,1)
        Ax = [self.__call__(t)[0] for t in tarr]
        plt.plot(tarr, Ax, label=r'$A_x$', **kwrds)
        plt.xlabel(r'$t, s$', fontsize=24)
        plt.ylim(1.1*min(Ax), 1.1 * max(Ax))
        plt.subplot(1,2,2)
        Ay = [self.__call__(t)[1] for t in tarr]
        plt.plot(tarr, Ay, label=r'$A_y$', **kwrds)
        plt.xlabel(r'$t, s$', fontsize=24)
        plt.ylim(1.1 * min(Ay), 1.1 * max(Ay))
    
    def make_fourier_transform(self, tarr):
        
        Ax = [self.__call__(t)[0] for t in tarr]
        Ay = [self.__call__(t)[1] for t in tarr]

        Axfft = np.fft.fft(np.array(Ax))
        Ayfft = np.fft.fft(np.array(Ay))
        return Axfft, Ayfft

    def plot_fourier_transform(self, trange=None, scale='log', **kwrds):
        '''
         scale = 'log' logarithmic scale
         scale = 'lin' linear scale
        '''
        
        if trange is None:
            tarr = np.linspace(-0.1 / self.frequency, 7 * np.pi / self.frequency, 100)
        else:
            tarr = trange

        Axfft, Ayfft = self.make_fourier_transform(tarr)
        #energy = 2. * np.pi / trange * 4.1357 * 10**(-15)
        
        n = tarr.size
        time_step = tarr[1]-tarr[0]

        energy = np.fft.fftfreq(n, d=time_step) * 4.1357 * 10**(-15) 
        
        max_en = max(energy)
        for i in xrange(0, len(energy)):
           if energy[i]<0:
              energy[i] += 2.*max_en

        plt.subplot(1,2,1)        
        if scale=='lin':
           plt.plot(energy, abs(Axfft),label='Ax_fft', **kwrds)
        elif scale=='log':
           try:
               plt.semilogy(energy, abs(Axfft), label='Ax_fft', **kwrds)
           except:
               pass
        plt.ylabel('Ax_fft')
        plt.xlabel('energy (eV)')
        
        plt.subplot(1,2,2)        
        if scale=='lin':
           plt.plot(energy, abs(Ayfft),label='Ay_fft', **kwrds)
        elif scale=='log':
           try:
               plt.semilogy(energy, abs(Ayfft), label='Ay_fft', **kwrds)
           except:
               pass
        plt.ylabel('Ay_fft')
        plt.xlabel('energy (eV)')
    
    def plot_envelope(self, trange=None):
        
        if trange is None:
            tarr = np.linspace(-0.1 / self.frequency, 7 * np.pi / self.frequency, 100)
        else:
            tarr = trange
        
        plt.subplot(1,2,1)
        A = [self.amplitude / self.frequency *\
             self.direction[0] * self.envelope(t) for t in tarr]
        plt.plot(tarr, A, '--')
        plt.subplot(1,2,2)
        A = [self.amplitude / self.frequency *\
             self.direction[1] * self.envelope(t) for t in tarr]
        plt.plot(tarr, A, '--')
        

class VectorPotentialWave(VectorPotential):
    
    def __init__(self, amplitude_E0, frequency, direction=[1.0,0.0], polarization='lin'):
        
        """
        amplitude_E0: is a maximum field strength
        """
        self.amplitude= amplitude_E0
        self.frequency = frequency
        norm = np.sqrt(direction[0]**2+direction[1]**2)
        self.direction = np.array(direction)/norm
        
    def __call__(self, t):
        VecPot = self.amplitude / self.frequency * np.sin(self.frequency * t)
        return [VecPot * self.direction[0], VecPot * self.direction[1]]
       
    
class FlatTopPulse(VectorPotential):
    
    def __init__(self, amplitude_E0, frequency, Tramp=None, duration=1.0, direction=[1.0,0.0], polarization='lin'):
        
        """
        amplitude_E0: is the maximum field strength
        """
        self.amplitude= amplitude_E0
        self.frequency = frequency
        norm = np.sqrt(direction[0]**2+direction[1]**2)
        self.direction = np.array(direction)/norm
        
        if Tramp is None:
           self.Tramp = np.pi/self.frequency
        else:
           self.Tramp = Tramp
        print self.Tramp
        self.pulse_duration = duration

    def envelope(self, t):
        
        if t < 0 or t > self.pulse_duration + 2.*self.Tramp:
            return 0.0
        elif t >= 0 and t <= self.Tramp:
            
            return t / self.Tramp
        elif t > self.pulse_duration + self.Tramp:
            return 2 + (self.pulse_duration - t) / self.Tramp 
        else:
            return 1.0
    
       
    def __call__(self, t):
        
        env = self.envelope(t)
        VecPot = self.amplitude / self.frequency * np.sin(self.frequency * t) * env
        return [VecPot * self.direction[0], VecPot * self.direction[1]]
    

# end class FlatTopPulse
    
class SinSqEnvelopePulse(VectorPotential):
    
    def __init__(self, amplitude_E0, frequency, Nc=1, cep=0.0, direction=[1.0,0.0], polarization='lin'): 
        
        """
        This class contains vector potential of a laser field
        with a sin^2 envelope 
        
        amplitude_E0: is the peak filed strength
        
        frequency: pulse frequency
        
        Nc: number of cycles
        """
        self.amplitude= amplitude_E0
        self.frequency = frequency
        self.Nc = Nc
        self.pulse_duration = 2. * self.Nc * np.pi / self.frequency
        norm = np.sqrt(direction[0]**2 + direction[1]**2)
        self.direction = np.array(direction) / norm
        self.CEP = cep
    
    def envelope(self, t):
        
        if t >= 0 and t < self.pulse_duration:
            return  np.sin(self.frequency * t / 2./self.Nc)**2
        else:
           return 0.0

    def __call__(self, t):
        
        env = self.envelope(t)
         
        VecPot = -self.amplitude / self.frequency *\
                  np.sin(self.frequency * t + self.CEP) * env
        return [VecPot * self.direction[0], VecPot * self.direction[1]]
        
# end class SinSqEnvelopePulse

class GaussianEnvelopePulse(VectorPotential):
    
    def __init__(self, amplitude_E0, frequency, t0=None, tc=None, Nc=1, cep=0.0, direction=[1.0,0.0], polarization='lin'):
        
        """
        This class contains vector potential of a laser field
        with a gaussian envelope 
        
        amplitude_E0: is the peak filed strength
        
        frequency: pulse frequency
        
        t0: standard deviation of gaussian; FWHM = 1.177 * t0
        t0 = 2. * Nc / self.frequency

        tc: center of the Gaussian
        tc = 1.8 * (np.pi * Nc / self.frequency)
        """
        
        self.amplitude= amplitude_E0
        self.frequency = frequency
        self.pulse_duration = 2. * Nc * np.pi / self.frequency
        if t0 is None:
            self.t0 = np.pi / 2.0 * Nc / self.frequency
        else:
            self.t0 = t0
        if tc is None:
            self.tc = 1.2 * np.pi * Nc / self.frequency
        else:
            self.tc = tc
        norm = np.sqrt(direction[0]**2 + direction[1]**2)
        self.direction = np.array(direction) / norm
        self.CEP = cep
    
    def envelope(self, t):
        return math.exp(-((t-self.tc)/self.t0)**2/0.7213)

    def __call__(self, t):
        env = self.envelope(t)
        VecPot = -self.amplitude / self.frequency *\
                 math.sin(self.frequency * t + self.CEP) * env
        return [VecPot * self.direction[0], VecPot * self.direction[1]]
        
# end class GaussianEnvelopePulse
