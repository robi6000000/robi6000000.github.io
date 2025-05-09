from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linprog


class Model:
    """
    Parent class of all models.
    """
    y: np.ndarray
    x_vect: np.ndarray
    var_count: int
    x_dim: int
    space_dim: int
    _beta: np.ndarray
    model_type: str

    def __init__(self, dependent_vect: np.ndarray, independent_vect: np.ndarray) -> None:
        """
        Records all variables needed for solving.
        :param dependent_vect: Vector with values of dependent variable
        :param independent_vect: Matrix of all independent variables... each variable is a row
        """
        # dependent vector of variables
        self.y = dependent_vect
        # list of independent vectors of variables
        self.x_vect = independent_vect
        # number of elements in a vector
        self.var_count = len(self.y)
        # dimension of x-es
        self.x_dim = len(independent_vect)
        # total space dimension
        self.space_dim = self.x_dim + 1
        # all attributes of solved problem
        # beta values
        self._beta = np.empty(1)
        # set model_type
        self.model_type = ""

    def r2(self) -> float:
        """
        Calculates the r2 of the value.
        :return: r2 value
        """

        if len(self.beta) == 0:
            print('Model is not solved')
            return 0.0

        y_hat = self.beta[0] + self.x_vect.transpose() @ self.beta[1:]
        y_mean = np.mean(self.y)

        res1 = 0
        res2 = 0

        res1 = np.sum((self.y - y_hat)**2)
        res2 = np.sum((self.y - y_mean)**2)

        result = 1 - (res1 / res2)
        return result

    @property
    def beta(self):
        """
        Prints a warning if model is not solved yet
        :return: beta values
        """
        if len(self._beta) == 0:
            print('WARNING: Model is not solved')
        return self._beta

    def visualize(self, save_loc='') -> bool:
        """
        Tries to visualize the model. Only works for 2D, 3D
        :param save_loc: save location, if not specified then plot.show()
        :return: bool of success
        """
        if self.space_dim == 3:
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            self._3d_plot(ax, save_loc)
            return True

        if self.space_dim == 2:
            fig, axes = plt.subplots()
            axes.set_xlim(0, 120)
            axes.set_ylim(0, 320)
            self._2d_plot(axes, save_loc)
            return True

        print('Model must be 2D or 3D')
        return False

    def _2d_plot(self, ax, save_loc) -> None:
        """
        Generates 2D plot of the model fitting.
        :param ax: axes
        :param save_loc: save location
        """
        ax.scatter(*self.x_vect, self.y)
        beta0, beta1 = self._beta
        left, right = ax.get_xlim()
        reg = [left * beta1 + beta0, right * beta1 + beta0]
        ax.plot([left, right], reg, label=self.model_type, c='r')
        ax.legend()

        plt.grid(True, linestyle='--', alpha=0.7)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.title(f'Data fitting using {self.model_type}')

        if save_loc != '':
            plt.savefig(save_loc)
        else:
            plt.show()

    def _3d_plot(self, ax, save_loc) -> None:
        """
        Generates 3D plot of model fitting.
        :param ax: axes
        :param save_loc: save location
        """
        ax.scatter(*self.x_vect, self.y, c='r')
        beta0, beta1, beta2 = self.beta
        x1, x2 = np.meshgrid(*self.x_vect)
        reg = beta0 + x1 * beta1 + x2 * beta2

        ax.plot_surface(x1, x2, reg, cmap='Blues')
        ax.set_title(f'Data fitting using {self.model_type}')

        if save_loc != '':
            plt.savefig(save_loc)
        else:
            plt.show()


class L1Model(Model):
    """
    Data fitting model using L1 norm.
    """

    def __init__(self, dependent_vect: np.ndarray, independent_vect: np.ndarray):
        super().__init__(dependent_vect, independent_vect)
        self.model_type = 'Manhattan norm'

    def solve(self) -> np.ndarray:
        """
        Solves the L1 linear programming problem.
        :return: array of beta values
        """
        # form LP
        c = np.concatenate(([0] * self.space_dim, np.ones(self.var_count)))
        A = np.vstack([np.array([1] * self.var_count), self.x_vect]).transpose()
        I = np.identity(self.var_count)
        A_ub = np.block([[-A, -I], [A, -I]])
        b_ub = np.concatenate([-self.y, self.y])
        # set bounds
        beta_bounds = [(None, None) for _ in range(self.space_dim)]
        t_bounds = [(0, None) for _ in range(self.var_count)]
        bounds = beta_bounds + t_bounds
        # solve
        solved = linprog(c, A_ub, b_ub, bounds=bounds)
        self._beta = solved.x[: self.space_dim]
        return self._beta


class LInfModel(Model):
    """
    Data fitting model using L infinity norm.
    """

    def __init__(self, dependent_vect: np.ndarray, independent_vect: np.ndarray):
        super().__init__(dependent_vect, independent_vect)
        self.model_type = 'Chebysev\'s norm'

    def solve(self) -> np.ndarray:
        """
        Solves the L infinity linear programming problem.
        :return: array of beta values
        """
        # form LP
        c = np.array([0] * self.space_dim + [1])
        A = np.vstack([np.array([1] * self.var_count), self.x_vect]).transpose()
        ones = np.ones((self.var_count, 1))
        A_ub = np.block([[-A, -ones], [A, -ones]])
        b_ub = np.concatenate([-self.y, self.y])
        # bounds
        beta_bounds = [(None, None) for _ in range(self.space_dim)]
        t_bounds = [(0, None)]
        bounds = beta_bounds + t_bounds
        # solve
        solved = linprog(c, A_ub, b_ub, bounds=bounds)
        self._beta = solved.x[: self.space_dim]
        return self._beta



class WeightedL1LInfModel(Model):
    """
    Data fitting model using L infinity norm.
    """

    def __init__(self, dependent_vect: np.ndarray, independent_vect: np.ndarray):
        super().__init__(dependent_vect, independent_vect)
        self.model_type = 'Weighted sum of L1 and LInf'

    def solve(self, omega: float) -> np.ndarray:
        """
        Minimizes sum of L1 and weighted L infinity linear programming problem.
        :param omega: weight for L1 norm, between 0 and 1
        :return: array of beta values
        """
        # check if omega is between 0 and 1
        if omega < 0 or omega > 1:
            raise ValueError('omega argument should be between 0 and 1')
        
        self.model_type += f', omega={omega}'
        
        # form LP
        c = np.array([0] * self.space_dim + [omega] * self.var_count + [1 - omega])
        A = np.vstack([np.array([1] * self.var_count), self.x_vect]).transpose()
        I = np.identity(self.var_count)
        ones = np.ones((self.var_count, 1))
        zero_matrix = I * 0
        zeroes = ones * 0
        
        A_ub = np.block([[-A, -I, zeroes], 
                         [A, -I, zeroes],
                         [-A, zero_matrix, -ones],
                         [A, zero_matrix, -ones]])
        b_ub = np.concatenate([-self.y, self.y, -self.y, self.y])
        # bounds
        beta_bounds = [(None, None) for _ in range(self.space_dim)]
        t_bounds = [(0, None) for _ in range(self.var_count)]
        gamma_bounds = [(0, None)]
        bounds = beta_bounds + t_bounds + gamma_bounds
        # solve
        solved = linprog(c, A_ub, b_ub, bounds=bounds)
        self._beta = solved.x[: self.space_dim]
        return self._beta
