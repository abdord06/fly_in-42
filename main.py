import sys
from src.gui import Visualizer
from src.parser import Parser
from src.simulation import Simulation


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <map_file.txt>")
        return

    map_file = sys.argv[1]

    try:
        parser = Parser(map_file)
        my_map = parser.parse()

        sim = Simulation(my_map)

        sim.run_and_print()
        visualise = Visualizer(sim.map, sim.drone_paths)
        visualise.run()

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
