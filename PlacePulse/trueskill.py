from math import sqrt
from scipy.special import erfinv
import math

class TrueSkill:
  def __init__(self, mu0, std0, std_factor, beta2, tau2, prob_draw):
    self.mu0 = mu0
    self.std0 = std0
    self.std_factor = std_factor
    self.beta2 = beta2 # rating class width
    self.tau2 = tau2 # additive dynamics
    self.draw_margin = TrueSkill._inv_cdf((prob_draw + 1.0)/2.0)*sqrt(2*beta2) # the draw margin

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


    # perform update of mu's and sigma's
    c = sqrt(2*self.beta2 + var_winner + var_loser)
    t = (mu_winner - mu_loser)/c
    eps = self.draw_margin/c
    if isDraw:
      v = TrueSkill._v_draw(t, eps)
      w = TrueSkill._w_draw(t, eps)
    else:
      v = TrueSkill._v_nondraw(t, eps)
      w = TrueSkill._w_nondraw(t, eps)

    mu_winner += var_winner*v/c
    mu_loser -= var_loser*v/c
    var_winner = var_winner * (1.0 - var_winner*w/(c**2))
    var_loser = var_loser * (1.0 - var_loser*w/(c**2))

    return ((mu_winner, math.sqrt(var_winner)), (mu_loser, math.sqrt(var_loser)))

  @staticmethod
  def _inv_cdf(prob):
    return sqrt(2.0)*erfinv(2*prob - 1.0)

  @staticmethod
  def _normpdf(x):
    return math.exp(-x**2/2)/sqrt(2*math.pi)
  
  @staticmethod
  def _normcdf(x):
    return 0.5*(1+math.erf(x/sqrt(2)))
  @staticmethod
  def _v_nondraw(t, eps):
    return TrueSkill._normpdf(t-eps)/TrueSkill._normcdf(t-eps)

  @staticmethod
  def _v_draw(t, eps):
    return (TrueSkill._normpdf(-eps-t) - TrueSkill._normpdf(eps-t))/(TrueSkill._normcdf(eps-t) - TrueSkill._normcdf(-eps-t))

  @staticmethod
  def _w_nondraw(t, eps):
    return TrueSkill._v_nondraw(t,eps)*(TrueSkill._v_nondraw(t,eps) + t -eps)

  @staticmethod
  def _w_draw(t, eps):
    return TrueSkill._v_draw(t,eps)**2 + ((eps-t)*TrueSkill._normpdf(eps-t) + \
      (eps+t)*TrueSkill._normpdf(eps+t))/(TrueSkill._normcdf(eps-t)-TrueSkill._normcdf(-eps-t))


# TrueSkill constants
MU0 = 25.0
STD_FACTOR = 3
STD0 = MU0/STD_FACTOR
BETA2 = (STD0**2)/4.0
TAU2 = (STD0**2)/10000
PROB_DRAW = 0.15

# a singleton object
trueskill = TrueSkill(MU0, STD0, STD_FACTOR, BETA2, TAU2, PROB_DRAW)