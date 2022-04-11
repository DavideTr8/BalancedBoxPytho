from printer import Plotter
from pathlib import Path

home_path = Path("/home/da_orobix/PycharmProjects/BalancedBoxPython")

actual_sol_path = (
    home_path
    / "BOMIP/Part II- Mixed Integer Programs/nondominated frontiers/Before post-processing/"
)
my_sol_path = home_path / "my_solutions"
my_images = home_path / "images"

problem_name = "First problem"
instance_name = "C160"


for solution_num in range(16, 21):
    solution_num = str(solution_num)
    actual_path_full = (
        actual_sol_path / problem_name / instance_name / (solution_num + "out.txt")
    )
    my_path_full = (
        my_sol_path / problem_name / instance_name / (solution_num + "dat.txt")
    )

    scatter_style = {
        "s": 2,
    }
    plot_style = {"linewidth": 1}
    plotter = Plotter(
        resolution=800, plot_style=plot_style, scatter_style=scatter_style
    )

    my_solution_dict = {}
    with open(my_path_full, "r") as rfile:
        for line in rfile:
            try:
                v1, v2, conn = line.split()
                v1 = float(v1)
                v2 = float(v2)
                conn = int(conn)
                my_solution_dict[(v1, v2)] = conn
            except ValueError as e:
                print(e)
                break

    plotter.plot_solutions(
        my_solution_dict,
        save_path=my_images
        / ("_".join([problem_name, instance_name, solution_num + "mine.png"])),
    )

    their_solution_dict = {}
    with open(actual_path_full, "r") as rfile:
        for line in rfile:
            try:
                v1, v2, conn = line.split()
                v1 = float(v1)
                v2 = float(v2)
                conn = int(conn)
                their_solution_dict[(v1, v2)] = conn
            except ValueError as e:
                print(e)
                break

    plotter.plot_solutions(
        their_solution_dict,
        save_path=my_images
        / ("_".join([problem_name, instance_name, solution_num + "their.png"])),
    )
