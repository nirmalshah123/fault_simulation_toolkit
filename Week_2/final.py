from argparse import ArgumentParser
import matplotlib.pyplot as plt
from PySpice.Spice.Netlist import Circuit
from time import perf_counter
import numpy as np


class ckt():
    def __init__(self, args, r1="1k", r2="1k"):
        self.circuit = Circuit(args.title)
        self.circuit.R('1', 1, 2, r1)
        self.circuit.R('2', 2, 0, r2)
        self.circuit.V('1', 1, 0, args.voltage)
        self.simulator = self.circuit.simulator(
            temperature=25, nominal_temperature=25)

    def run(self):
        ans = np.array([])
        for i in range(1000):
            self.analysis = self.simulator.operating_point()
            ans = np.append(ans, float(self.analysis.nodes['2']))
            self.circuit.R1.resistance = (str(1+i) + "k")
        return (ans)

    def plot(self):
        y = self.run()
        for i in y:
            plt.plot(i, '*')
        plt.savefig('sims_result_seq.png')


if __name__ == "__main__":
    p = ArgumentParser(description='Simulation')
    p.add_argument('-o', '--output', type=str,
                   default="None", help='File name')
    p.add_argument('--tol', type=float, default=10,
                   help='Enter tolerance level of the resistors')
    p.add_argument('-v', '--voltage', type=float, default=3.3,
                   help='Enter voltage source value')
    p.add_argument('--temp', type=float, default=25, help='Enter temperature')
    p.add_argument('--title', type=str, default="Simulation",
                   help='Enter title of the circuit')

    args = p.parse_args()
    obj1 = ckt(args=args)
    start = perf_counter()
    obj1.plot()
    print(perf_counter()-start)
