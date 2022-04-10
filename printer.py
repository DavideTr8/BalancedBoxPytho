import matplotlib

matplotlib.use("TkAgg")
from matplotlib import pyplot as plt


class Writer:
    def __init__(self, problem_type, solution_path):
        self.problem_type = problem_type
        self.solution_path = solution_path

    def print_solution(self, solutions_dict, tot_time=None, iterations=None):
        if self.problem_type == "max":
            sol_list = [(-x[0], -x[1], solutions_dict[x]) for x in solutions_dict]
        else:
            sol_list = [(x[0], x[1], solutions_dict[x]) for x in solutions_dict]

        with open(self.solution_path, "w") as sfile:
            for sol in sol_list:
                sfile.write(f"{sol[0]}\t{sol[1]}\t{sol[2]}\n")
            if tot_time is not None:
                sfile.write(f"Time={tot_time}\n")
            if iterations is not None:
                sfile.write(f"Iterations={iterations}\n")


class Plotter:
    def __init__(self, resolution, plot_style, scatter_style):
        self.resolution = resolution
        self.plot_style = plot_style
        self.scatter_style = scatter_style

    def plot_solutions(self, sol_dict, save_path=None):
        plt.figure()
        plt.scatter(
            [x[0] for x in sol_dict], [x[1] for x in sol_dict], **self.scatter_style
        )
        keys = list(sol_dict.keys())
        for item_idx in range(len(sol_dict) - 1):
            key = keys[item_idx]
            if sol_dict[key] == 1:
                next_key = keys[item_idx + 1]
                plt.plot(
                    [key[0], next_key[0]], [key[1], next_key[1]], **self.plot_style
                )
        if save_path is not None:
            plt.savefig(save_path, dpi=self.resolution)
        else:
            plt.show()
        plt.clf()
