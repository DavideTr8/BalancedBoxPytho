import BOIP
import argparse
import logging

logging.basicConfig(level=20)

parser = argparse.ArgumentParser("BOIP parser")
parser.add_argument("problem", type=str)
parser.add_argument("problem_class", type=str)
parser.add_argument("instance", type=str)

args = parser.parse_args()

instances = {
    "class A": ["1dat.txt", "2dat.txt", "3dat.txt", "4dat.txt", "5dat.txt"],
    "class B": ["6dat.txt", "7dat.txt", "8dat.txt", "9dat.txt", "10dat.txt"],
    "class C": ["11dat.txt", "12dat.txt", "13dat.txt", "14dat.txt", "15dat.txt"],
    "class D": ["16dat.txt", "17dat.txt", "18dat.txt", "19dat.txt", "20dat.txt"],
}

for pclass in instances:
    for instance in instances[pclass]:
        logging.info(
            f"Running problem {args.problem}, class {pclass}, instance {instance}"
        )
        BOIP.main(problem=args.problem, problem_class=pclass, instance=instance)
