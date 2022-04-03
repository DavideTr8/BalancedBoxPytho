import BOIP
import BOMIP
import argparse
import logging

logging.basicConfig(level=20)

parser = argparse.ArgumentParser("BOIP parser")
parser.add_argument("-problem", type=str)
parser.add_argument("-problem_class", type=str)
parser.add_argument("-instance", type=str)

parser.add_argument("--run_all", action="store_true")

args = parser.parse_args()

boip_problems = ["2DKP", "AP"]
if args.problem in boip_problems:
    problem_type = BOIP
    instances = {
        "class A": ["1dat.txt", "2dat.txt", "3dat.txt", "4dat.txt", "5dat.txt"],
        "class B": ["7dat.txt", "8dat.txt", "9dat.txt", "10dat.txt"],
        "class C": ["11dat.txt", "12dat.txt", "13dat.txt", "14dat.txt", "15dat.txt"],
        "class D": ["17dat.txt", "18dat.txt", "19dat.txt", "20dat.txt"],
    }
else:
    problem_type = BOMIP
    instances = {
        # "C20": ["3dat.txt", "4dat.txt", "5dat.txt"], #["1dat.txt", "2dat.txt",
        # "C40": ["6dat.txt", "7dat.txt", "8dat.txt", "9dat.txt", "10dat.txt"],
        # "C80": ["11dat.txt", "12dat.txt", "13dat.txt", "14dat.txt", "15dat.txt"],
        "C160": ["16dat.txt", "17dat.txt", "18dat.txt", "19dat.txt", "20dat.txt"],
        # "C320": ["21dat.txt", "22dat.txt", "23dat.txt", "24dat.txt", "25dat.txt"]
    }

if args.run_all:
    for pclass in instances:
        for instance in instances[pclass]:
            logging.info(
                f"Running problem {args.problem}, class {pclass}, instance {instance}"
            )
            problem_type.main(
                problem=args.problem, problem_class=pclass, instance=instance
            )

else:
    problem_type.main(
        problem=args.problem, problem_class=args.problem_class, instance=args.instance
    )
