import matplotlib.pyplot as plt
from PySpice.Doc.ExampleTools import find_libraries
from PySpice.Probe.Plot import plot
from PySpice.Spice.Library import SpiceLibrary
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
import numpy as np
import os
import multiprocessing as mp
import asyncio
import random
from time import perf_counter
import json
from argparse import ArgumentParser
import netlist


circuit = Circuit("Sims")
global_cases = []

async def ckt_gen(circuit,params):

    for i in params:
        if(i == 'M'):
            for j in params[i]:
                j.model = params[i][j][0]
                j.length = params[i][j][1]
                j.width = params[i][j][2]
        elif(i == 'R'):
            for j in params[i]:
                j.resistance = params[i][j]
        elif(i == 'C'):
            for j in params[i]:
                j.capacitance = params[i][j]
    simulator = circuit.simulator(
        temperature=25, nominal_temperature=25)
    analysis = simulator.operating_point()
    return ([analysis.branches, analysis.nodes])

async def run(index, no_of_threads):
    circuit = globals()['circuit']
    tasks = []
    for i in range(no_of_threads):
        tasks.append(asyncio.create_task(
            ckt_gen(circuit = circuit,params = global_cases[i+index])))
    ans = await asyncio.gather(*tasks)
    return (ans)

def child(index, no_of_threads):
    ans = asyncio.run(run(index, no_of_threads))
    return (ans)


def save(file_name, res):
    index=0
    result = {}
    result['current'] = {}
    result['voltage'] = {}
    for i in range(0,len(res)-1,2):
        result['current'][index] = {}
        result['voltage'][index] = {}
        current = res[i]
        voltage = res[i+1]
        temp = {}
        for j in current.keys():
            temp[j] = list(np.array(current[j]))
        result['current'][index] = temp
        temp = {}
        for j in voltage.keys():
            temp[j]  = list(np.array(voltage[j]))
        result['voltage'][index] = temp
        index+=1

    with open(file_name, 'w') as f:
        json.dump(result,f, indent=2)  


class monte_carlo_sims():
    '''
        This class is used to perform monte carlo simulations
        Inputs:-
        circuit = Provide the circuit object on which Monte carlo simulations need to be performed
        no_of_simulations = Total number of simulations needed to be performed
        tol = tolerence for the elements(Assumed to be equal for all the elements)
        path = Path to all the spice files

    '''


    def __init__(self, circuit, file_name, spice_library, no_of_simulations=2, tol=10):
        self.circuit = circuit
        self.no_of_simulations = no_of_simulations
        self.resistors = []
        self.mosfet_nmos = []
        self.mosfet_pmos = []
        self.capacitors = []
        self.libraries_nmos = []
        self.libraries_pmos = []
        self.cases = [] 
        self.result = np.array([])
        self.path_to_library(spice_library)
        self.segregate()
        self.create_sims(tol)
        self.solve()
        save(file_name, self.result)
    

    def path_to_library(self,spice_library):
        for i in spice_library:
            if('pmos' in  i):
                self.libraries_pmos.append(i)
            else:
                self.libraries_nmos.append(i)

    def segregate(self):
        for i in list(self.circuit.element_names):
            if(i[0] == 'R'):
                self.resistors.append(self.circuit[i])
            elif(i[0] == 'M' and (circuit[i].model[0] == 'n')):
                self.mosfet_nmos.append(self.circuit[i])
            elif(i[0] == 'M' and (circuit[i].model[0] == 'p')):
                self.mosfet_pmos.append(self.circuit[i])
            elif(i[0] == 'C'):
                self.capacitors.append(self.circuit[i])
            
    
    def create_sims(self, tol):
        for i in range(self.no_of_simulations):
            tasks = {}
            tasks['M'] = {}
            tasks['R'] = {}
            tasks['C'] = {}
            model_nmos = self.libraries_nmos[np.random.randint(0,len(self.libraries_nmos))]
            model_pmos = self.libraries_pmos[np.random.randint(0,len(self.libraries_pmos))]
            for j in self.mosfet_nmos:
                length = str(float(j.length[:-1]) + (np.random.rand()*tol/100)) + 'u'
                width = str(float(j.width[:-1]) + (np.random.rand()*tol/100)) + 'u'
                tasks['M'][j] = [model_nmos, length, width]
            for j in self.mosfet_pmos:
                length = str(float(j.length[:-1]) + (np.random.rand()*tol/100)) + 'u'
                width = str(float(j.width[:-1]) + (np.random.rand()*tol/100)) + 'u'
                tasks['M'][j] = [model_pmos, length, width] 
            for j in self.resistors:
                tasks['R'][j] = str(float(j.resistance[:-1]) + (np.random.rand()*tol/100))+'k'
            for j in self.capacitors:
                tasks['C'][j] = str(float(j.resistance[:-1]) + (np.random.rand()*tol/100)) + 'u'
            global_cases.append(tasks)

    def solve(self):
        no_of_cpu = (os. cpu_count())
        pool = mp.Pool()
        threads_per_core = int(self.no_of_simulations/no_of_cpu)
        leftover_threads = self.no_of_simulations - (threads_per_core*no_of_cpu)

        if (self.no_of_simulations < 12):
            a = [pool.apply_async(child, args=(i, 1)) for i in range(self.no_of_simulations)]
            pool.close()
            pool.join()
        else:
            index = np.arange(0, self.no_of_simulations, threads_per_core)
            a = [pool.apply_async(child, args=(index[i], threads_per_core))
                for i in range(no_of_cpu)]
            pool.close()
            pool.join()
            if (leftover_threads != 0):
                b = child(threads_per_core*no_of_cpu, leftover_threads)
                self.result = np.append(self.result, b)
        

        for i in a:
            self.result = np.append(self.result, i.get())
            
        
class op():
    def __init__(self, circuit, file_name):
        self.circuit = circuit
        self.solve()
        save(file_name,self.result)
    
    def solve(self):
        simulator = self.circuit.simulator(
        temperature=25, nominal_temperature=25)
        analysis = simulator.operating_point()
        self.result = [analysis.branches, analysis.nodes]
        

class process_corner_sims():
    def __init__(self, circuit, spice_library, file_name):
        self.circuit = circuit
        self.libraries_nmos = []
        self.libraries_pmos = []
        self.mosfet_nmos = []
        self.mosfet_pmos = []
        self.result = []
        for i in spice_library:
            if('pmos' in  i):
                self.libraries_pmos.append(i)
            else:
                self.libraries_nmos.append(i)
        self.simulator = self.circuit.simulator(
        temperature=25, nominal_temperature=25)
        self.segregate()
        self.solve()
        save(file_name, self.result)

    def segregate(self):
        for i in list(self.circuit.element_names):
            if(i[0] == 'M' and (circuit[i].model[0] == 'n')):
                self.mosfet_nmos.append(self.circuit[i])
            elif(i[0] == 'M' and (circuit[i].model[0] == 'p')):
                self.mosfet_pmos.append(self.circuit[i])

    def solve(self):
        if(len(self.mosfet_nmos) == 0):
            for j in self.libraries_pmos:
                for k in self.mosfet_pmos:
                    k.model = j
                analysis = self.simulator.operating_point()
                self.result.append(analysis.branches)
                self.result.append(analysis.nodes)
        elif(len(self.mosfet_pmos) == 0):
            for j in self.libraries_nmos:
                for k in self.mosfet_nmos:
                    k.model = j
                analysis = self.simulator.operating_point()
                self.result.append(analysis.branches)
                self.result.append(analysis.nodes)   
        else:               
            for i in self.libraries_nmos:
                for j in self.libraries_pmos:
                    for k in self.mosfet_nmos:
                        k.model = i
                    for k in self.mosfet_pmos:
                        k.model = j
                    analysis = self.simulator.operating_point()
                    self.result.append(analysis.branches)
                    self.result.append(analysis.nodes)

if __name__=="__main__":
    circuit = globals()['circuit']
    circuit = netlist.circuit
    libraries_path = "./"
    spice_library = SpiceLibrary(libraries_path)
    p = ArgumentParser(description='Analog Circuit Simulator')
    p.add_argument('--sim', type=str, default='op',choices=['op', 'mc', 'pc'], help='Which type of simulation to be performed')
    p.add_argument('-o', '--output', type=str, default="None", help='File name (JSON format)')
    p.add_argument('-n', '--nsims', type=int, default=100, help="Enter number of simulations for Monte Carlo")
    p.add_argument('-t', '--tol', type=float, default=10, help="Enter tolerence for each element")

    args = p.parse_args()
    if(args.sim == 'pc'):
        obj = process_corner_sims(circuit, list(spice_library.models), file_name='result.json')
    elif(args.sim == 'op'):
        obj = op(circuit=circuit, file_name=args.output)
    elif(args.sim == 'mc'):
        obj = monte_carlo_sims(circuit=circuit, file_name=args.output,spice_library=list(spice_library.models), no_of_simulations=args.nsims, tol=args.tol)

    