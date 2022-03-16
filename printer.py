import matplotlib

matplotlib.use("TkAgg")
from matplotlib import pyplot as plt


class Writer:
    def __init__(self, problem_type, solution_path):
        self.problem_type = problem_type
        self.solution_path = solution_path

    def print_solution(self, sol_list):
        if self.problem_type == "max":
            sol_list = [(-x[0], -x[1]) for x in sol_list]

        sorted_sols = sorted(sol_list, key=lambda x: x[0])

        with open(self.solution_path, "w") as sfile:
            for sol in sorted_sols:
                sfile.write(f"{sol[0]}\t{sol[1]}\n")


class Plotter:
    def __init__(self, plot_style):
        self.plot_style = plot_style

    def plot_solutions(self, sol_dict):
        plt.figure(0)
        plt.scatter([x[0] for x in sol_dict], [x[1] for x in sol_dict])
        keys = list(sol_dict.keys())
        for item_idx in range(len(sol_dict) - 1):
            key = keys[item_idx]
            if sol_dict[key] == 1:
                next_key = keys[item_idx + 1]
                plt.plot([key[0], next_key[0]], [key[1], next_key[1]])
        plt.show()
