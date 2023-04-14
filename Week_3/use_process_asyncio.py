import matplotlib.pyplot as plt
from PySpice.Spice.Netlist import Circuit
from time import perf_counter
import multiprocessing as mp
import asyncio
import os
import numpy as np


async def ckt_gen(circuit,params):
    # print(os.getpid())
    for i in params:
        i.resistance = params[i]
    simulator = circuit.simulator(
        temperature=25, nominal_temperature=25)
    analysis = simulator.operating_point()
    return (float(analysis.nodes['2']))


async def run(index, no_of_threads):
    circuit = Circuit("Sims")
    circuit.R('1', 1, 2, "1k")
    circuit.R('2', 2, 0, "1k")
    circuit.V('1', 1, 0, 3.3)
    params = {}
    resistors = []
    e = list(circuit.element_names)
    for i in e:
        if(i[0] == 'R'):
            resistors.append(circuit[i])
    tasks = []
    for i in range(no_of_threads):
        params[resistors[0]] = str(1+index+i)+"k"
        params[resistors[1]] = "1k"
        tasks.append(asyncio.create_task(
            ckt_gen(circuit = circuit, params = params)))
    ans = await asyncio.gather(*tasks)
    return (ans)


def child(index, no_of_threads):
    ans = asyncio.run(run(index, no_of_threads))
    return (ans)


if __name__ == '__main__':
    no_sims = 10000
    result = np.array([])
    no_of_cpu = (os. cpu_count())
    pool = mp.Pool()
    threads_per_core = int(no_sims/no_of_cpu)
    leftover_threads = no_sims - (threads_per_core*no_of_cpu)
    t1 = perf_counter()
    if (no_sims < 12):
        a = [pool.apply_async(child, args=(i, 1)) for i in range(no_sims)]
        pool.close()
        pool.join()
    else:
        index = np.arange(0, no_sims, threads_per_core)
        a = [pool.apply_async(child, args=(index[i], threads_per_core))
             for i in range(no_of_cpu)]
        pool.close()
        pool.join()
        if (leftover_threads != 0):
            b = child(threads_per_core*no_of_cpu, leftover_threads)
            result = np.append(result, b)
    for i in a:
        result = np.append(result, i.get())
    result = result.flatten()
    for i in result:
        plt.plot(i, '*')
    plt.savefig('sims_result_process_asyncio.png')
    t2 = perf_counter()
    print(t2-t1)
