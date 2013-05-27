from math import sqrt
from scipy.special import erfinv
from scipy.special import log_ndtr
from numpy import logaddexp
import math
import scipy.stats
import numpy as np

def logdiffexp(a, b):
  if a == b: return -1000
  return a + math.log(-np.expm1(b-a))

class TrueSkill:
  def __init__(self, mu0, std0, std_factor, beta2, tau2, prob_draw):
    self.mu0 = mu0
    self.std0 = std0
    self.std_factor = std_factor
    self.beta2 = beta2 # rating class width
    self.tau2 = tau2 # additive dynamics
    self.draw_margin = TrueSkill._inv_cdf((prob_draw + 1.0)/2.0)*sqrt(2*beta2 + 2*std0**2) # the draw margin

  def get_score(self, mu, std):
    # conservative rating: score is several std below the mean
    return mu - self.std_factor*std

  def update_rating(self, winner, loser, isDraw):
    # unpack data
    mu_winner, std_winner = winner
    var_winner = std_winner**2
    mu_loser, std_loser = loser
    var_loser = std_loser**2

    # before updates perform additive dynamics
    var_winner += self.tau2
    var_loser += self.tau2


    # precompute some values
    c = sqrt(2*self.beta2 + var_winner + var_loser)
    t = (mu_winner - mu_loser)/c
    eps = self.draw_margin/c
    logpdfmm = TrueSkill._logpdf(-eps-t)
    logpdfpp = logpdfmm
    logpdfpm = TrueSkill._logpdf(eps-t)
    logpdfmp = logpdfpm

    logcdfmm = TrueSkill._logcdf(-eps-t)
    logcdfpp = TrueSkill._logcdf(eps+t)
    logcdfpm = TrueSkill._logcdf(eps-t)
    logcdfmp = TrueSkill._logcdf(-eps+t)
    
    if isDraw:
      v = self._v_draw(t, logpdfmm, logpdfpm, logcdfmm, logcdfpm, logpdfmp, logpdfpp, logcdfmp, logcdfpp)
      w = self._w_draw(t, eps, logpdfmm, logpdfpm, logcdfmm, logcdfpm, logpdfmp, logpdfpp, logcdfmp, logcdfpp)
    else:
      v = self._v_nondraw(logpdfmp, logcdfmp)
      w = self._w_nondraw(t, eps, logpdfmp, logcdfmp)

    mu_winner += var_winner*v/c
    mu_loser -= var_loser*v/c
    var_winner *= (1.0 - var_winner*w/(c**2))
    var_loser *= (1.0 - var_loser*w/(c**2))

    return ((mu_winner, math.sqrt(var_winner)), (mu_loser, math.sqrt(var_loser)))

  @staticmethod
  def _inv_cdf(prob):
    return sqrt(2.0)*erfinv(2*prob - 1.0)

  @staticmethod
  def _logpdf(x):
    return 0.5*(-x**2 - math.log(2*math.pi))

  @staticmethod
  def _logcdf(x):
    #if x > 0: return math.log1p(-math.exp(TrueSkill.logcdf(-x)))  
    return log_ndtr(x)
    
  @staticmethod
  def _v_nondraw(logpdfmp, logcdfmp):
    return math.exp(logpdfmp - logcdfmp)

  @staticmethod
  def _v_draw(t, logpdfmm, logpdfpm, logcdfmm, logcdfpm, logpdfmp, logpdfpp, logcdfmp, logcdfpp):
    if t<0: return -TrueSkill._v_draw(-t, logpdfmp, logpdfpp, logcdfmp, logcdfpp, logpdfmm, logpdfpm, logcdfmm, logcdfpm)
    mul = 1.0
    if logpdfmm < logpdfpm:
      logpdfmm, logpdfpm = logpdfpm, logpdfmm
      mul = -mul
    if logcdfpm < logcdfmm:
      logcdfpm, logcdfmm = logcdfmm, logcdfpm
      mul = -mul
    return mul*math.exp(logdiffexp(logpdfmm, logpdfpm) - logdiffexp(logcdfpm, logcdfmm))

  @staticmethod
  def _w_nondraw(t, eps, logpdfmp, logcdfmp):
    vnondraw = TrueSkill._v_nondraw(logpdfmp, logcdfmp)
    return vnondraw*(vnondraw + t - eps)

  @staticmethod
  def _w_draw(t, eps, logpdfmm, logpdfpm, logcdfmm, logcdfpm, logpdfmp, logpdfpp, logcdfmp, logcdfpp):
    if t < 0: return TrueSkill._w_draw(-t, eps, logpdfmp, logpdfpp, logcdfmp, logcdfpp, logpdfmm, logpdfpm, logcdfmm, logcdfpm)
    sign = 1.0
    if eps - t > 0:
      logpm = math.log(eps - t)
    else:
      logpm = math.log(t-eps)
      sign = -sign
    logpp = math.log(eps + t)
    if sign == 1: loga = logaddexp(logpm + logpdfpm, logpp + logpdfpp)
    else:
      if logpm + logpdfpm > logpp + logpdfpp:
        loga = logdiffexp(logpm + logpdfpm, logpp + logpdfpp)
        sign = -1.0
      else:
        loga = logdiffexp(logpp + logpdfpp, logpm + logpdfpm)
        sign = 1.0
    logb = logdiffexp(logcdfpm, logcdfmm)
    vdraw = TrueSkill._v_draw(t, logpdfmm, logpdfpm, logcdfmm, logcdfpm, logpdfmp, logpdfpp, logcdfmp, logcdfpp)
    return vdraw**2  + sign*math.exp(loga - logb)


# TrueSkill constants
MU0 = 25.0
STD_FACTOR = 0.0
STD0 = MU0/3.0
BETA2 = (STD0**2)/4.0
TAU2 = (STD0**2)/10000
PROB_DRAW = 0.13

# a singleton object
trueskill = TrueSkill(MU0, STD0, STD_FACTOR, BETA2, TAU2, PROB_DRAW)