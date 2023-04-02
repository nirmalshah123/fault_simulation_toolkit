from argparse import ArgumentParser
import matplotlib.pyplot as plt
from PySpice.Spice.Netlist import Circuit
from time import perf_counter
import numpy as np
from threading import Thread


def ckt_gen(r1, r2, result, index):
    circuit = Circuit("Sims")
    circuit.R('1', 1, 2, r1)
    circuit.R('2', 2, 0, r2)
    circuit.V('1', 1, 0, 3.3)
    simulator = circuit.simulator(
        temperature=25, nominal_temperature=25)
    analysis = simulator.operating_point()
    result[index] = (float(analysis.nodes['2']))


if __name__ == "__main__":
    no_sims = 1000
    funcs = []
    ans = [None]*no_sims
    threads = [None]*no_sims
    for i in range(no_sims):
        threads[i] = Thread(target=ckt_gen, args=(str(1+i)+"1k", "1k", ans, i,))
    t1 = perf_counter()
    for i in threads:
        i.start()
        i.join()
    for i in ans:
        plt.plot(i, '*')
    plt.savefig('sims_result_thread.png')
    print(perf_counter()-t1)

