from argparse import ArgumentParser
import matplotlib.pyplot as plt
from PySpice.Spice.Netlist import Circuit
from time import perf_counter
import numpy as np
import asyncio


async def ckt_gen(r1="1k", r2="1k"):
    circuit = Circuit("Sims")
    circuit.R('1', 1, 2, r1)
    circuit.R('2', 2, 0, r2)
    circuit.V('1', 1, 0, 3.3)
    simulator = circuit.simulator(
        temperature=25, nominal_temperature=25)
    analysis = simulator.operating_point()
    return(float(analysis.nodes['2']))


async def main():
    no_sims = 1000
    funcs = []
    for i in range(no_sims):
        funcs.append(ckt_gen(r1=str(1+i)+"1k", r2="1k"))
    t1 = perf_counter()
    ans = await asyncio.gather(*funcs)

    for i in ans:
        plt.plot(i, '*')
    plt.savefig('sims_result_asyncio.png')
    print(perf_counter()-t1)

asyncio.run(main())
