from printer import Plotter
from pathlib import Path

home_path = Path("/home/da_orobix/PycharmProjects/BalancedBoxPython")
actual_sol_path = (
    home_path
    / "BOMIP/Part II- Mixed Integer Programs/nondominated frontiers/After post-processing/First problem/"
)
my_sol_path = home_path / "my_solutions" / "First problem"

solution_name = "3out.txt"
solution_path = actual_sol_path / "C20" / solution_name
scatter_style = {
    "s": 2,
}
plot_style = {"linewidth": 1}
plotter = Plotter(resolution=800, plot_style=plot_style, scatter_style=scatter_style)

solution_dict = {}
with open(solution_path, "r") as rfile:
    for line in rfile:
        v1, v2, conn = line.split()
        v1 = float(v1)
        v2 = float(v2)
        conn = int(conn)
        solution_dict[(v1, v2)] = conn

plotter.plot_solutions(
    solution_dict,
    save_path=actual_sol_path / "C20" / solution_name.replace("txt", "png"),
)
