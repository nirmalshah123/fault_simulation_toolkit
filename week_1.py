# week 1 update. Have understood the PySpice library,
# and have decided the functionalities to
# be added to the project. Prepared a basic
# flow plan about which functions to create
# In this file have added a voltage divider,
# and change their resistances using a for loop to see
# the effect at the output voltage due to process variation
from argparse import ArgumentParser
import matplotlib.pyplot as plt
from PySpice.Spice.Netlist import Circuit
from time import perf_counter


def set_up(args, r1, r2):
    circuit = Circuit("Simulation")
    circuit.R('1', 1, 2, r1)
    circuit.R('2', 2, 0, r2)
    circuit.V('1', 1, 0, args.voltage)
    return (circuit)


def sim(args):
    ans = []
    circuit = set_up(args, str(1) + "k", str(1) + "k")
    for i in range(5):
        circuit = set_up(args, str(1+i) + "k", str(1) + "k")
        simulator = circuit.simulator(temperature=25, nominal_temperature=25)
        analysis = simulator.dc(V1=slice(0, args.voltage, .01))
        ans.append(analysis["2"])
    return (ans, analysis["1"])


def plot():
    y, x = sim(args)
    for i in y:
        plt.plot(x, i)
    plt.savefig('sims_result.png')


p = ArgumentParser(description='Simulation')
p.add_argument('-o', '--output', type=str, default="None", help='File name')
p.add_argument('--tol', type=float, default=10,
               help='Enter tolerance level of the resistors')
p.add_argument('-v', '--voltage', type=float, default=3.3,
               help='Enter voltage source value')
p.add_argument('--temp', type=float, default=25, help='Enter temperature')

args = p.parse_args()

start = perf_counter()
plot()
stop = perf_counter()
print(stop - start)
