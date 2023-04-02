import matplotlib.pyplot as plt
from PySpice.Spice.Netlist import Circuit
from time import perf_counter
from multiprocessing import Process, Value


def ckt_gen(ans, r1="1k", r2="1k"):
    circuit = Circuit("Sims")
    circuit.R('1', 1, 2, r1)
    circuit.R('2', 2, 0, r2)
    circuit.V('1', 1, 0, 3.3)
    simulator = circuit.simulator(
        temperature=25, nominal_temperature=25)
    analysis = simulator.operating_point()
    ans.value = (float(analysis.nodes['2']))


if __name__ == "__main__":
    no_sims = 200
    ans = [Value('f', 0.0) for i in range(no_sims)]
    processes = [Process(target=ckt_gen, args=(ans[i],
                                               str(1+i)+"1k", "1k", )) for i in range(no_sims)]
    t1 = perf_counter()
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    for i in ans:
        plt.plot(i.value, '*')
    plt.savefig('sims_result_process.png')
    print(perf_counter()-t1)
