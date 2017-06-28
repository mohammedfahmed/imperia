# find cutoff distance for a certain configuration
import sympy
import scipy.constants

distance = sympy.symbols("distance")
frequency = 2347000000
noisefloor = 4
bandwidth = 1e6
txpower = 0
txantennagain = 0
rxantennagain = 0

expr_pathloss = 20*sympy.log(distance*frequency*4*sympy.pi/scipy.constants.c,10)
expr_rxpower = txpower + txantennagain + rxantennagain - expr_pathloss
expr_rxpowermin = -174 + noisefloor + 10*sympy.log(bandwidth,10)

# measured rxpower = SINR + noise floor
# measured SINR = 21.222434, 46.222435, 71.222435, 96.222435
# noise floor = -96.989700

sol = sympy.solveset(sympy.Eq(expr_rxpower,expr_rxpowermin),distance)
distance_sol = float(sol.args[0])

print(distance_sol)