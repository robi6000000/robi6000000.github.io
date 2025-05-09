import numpy as np
from scipy.optimize import linprog
import pandas as pd

#importing data and creating dataframes
data = pd.read_csv('data/A04wine.csv')

# Separate dependent variable (y) and independent variables (x)
y = data['Price']
x = data[['WinterRain','AGST', 'HarvestRain', 'Age', 'FrancePop']]
# Calculate the number of variables (features) plus 1 for the intercept term
k = x.shape[1]

#--------------------------------------------------------------------------------------------------

# Formulating the linear programming problem for L1 norm
c = np.concatenate(([0]*(k + 1), np.ones(len(x.values)))) # Objective function coefficients

A = np.block([np.ones((len(x.values), 1)), np.array(x.values)]) 
                            # Concatenate coefficients of variables into one matrix

I = np.identity(len(x.values)) # Identity matrix for values of vector t

# Formulate inequality constraints for L1 norm
A_ub = np.block([[-A, -I], [A, -I]])
b_ub = np.concatenate([-y, y])
bounds = [(None, None)]*(k + 1) +[(0, None)] * len(x.values)

# Solve the linear programming problem for L1 norm
solve = linprog(c, A_ub, b_ub, bounds=bounds)

# extract variables(betas) and print them out
betas = solve.x[:k+1]
print(betas)    #[-8.88e-01  1.58e-03  5.21e-01 -4.51e-03 1.13e-02 -2.21e-05]

#--------------------------------------------------------------------------------------------------

# Formulating the linear programming problem for L-inf norm
c_inf = np.concatenate(([0]*(k + 1), [1])) # Objective function coefficients

A_inf = np.block([np.ones((len(x.values), 1)), np.array(x.values)]) 
                        # Coefficients for independent variables for L-inf norm

i_inf = np.ones((len(x.values), 1)) # Coefficients for gamma scalar variable

# Formulate inequality constraints for L-inf norm
A_ub_inf = np.block([[-A_inf, -i_inf], [A_inf, -i_inf]])
b_ub_inf = np.concatenate([-y, y]) 
bounds_inf = [(None, None)]*(k + 1) + [(0, None)]

# Solve the linear programming problem for l-inf norm
solve_inf = linprog(c_inf, A_ub_inf, b_ub_inf, bounds=bounds_inf)

# extract betas and print them out
betas_inf = solve_inf.x[:k+1]
print(betas_inf)    # [3.48e+00  8.34e-04  6.00e-01 -3.34e-03 -2.30e-02 -1.20e-04]
