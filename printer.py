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

    def plot_solutions(self, sol_list):
        plt.plot([x[0] for x in sol_list], [x[1] for x in sol_list], self.plot_style)
