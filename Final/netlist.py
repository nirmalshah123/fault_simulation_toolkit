from PySpice.Doc.ExampleTools import find_libraries
from PySpice.Probe.Plot import plot
from PySpice.Spice.Library import SpiceLibrary
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit("Sims")
libraries_path = "./"
spice_library = SpiceLibrary(libraries_path)
circuit.title = "Diff Pair"
circuit.include(spice_library['nmos'])
Vdd = 2.2

circuit.V('gate_1', 'gatenode_1', circuit.gnd, 0.8)
circuit.V('gate_2', 'gatenode_2', circuit.gnd, 0.8)
circuit.R(1, 'drain_1', 'vdd', "20k")
circuit.R(2, 'drain_2', 'vdd', "20k")
circuit.V(1, 'vdd', circuit.gnd, u_V(Vdd))
circuit.I(1,'source', 0,'106u')
circuit.MOSFET(1, 'drain_1', 'gatenode_1', 'source', circuit.gnd, model='nmos', l = "1u", w="1u")
circuit.MOSFET(2, 'drain_2', 'gatenode_2', 'source', circuit.gnd, model='nmos', l = "1u", w="1u")
for r in (circuit.R1, circuit.R2):
    r.minus.add_current_probe(circuit)