from automan.api import Problem, Automator, Simulation
from matplotlib import pyplot as plt
import numpy as np
import json


class Simulator(Problem):
    def get_filtered_data(self):
        data = {}
        index = 0
        for i in self.cases:
            path = i.input_path('result.json')
            my_dict = {}
            with open(path, 'r') as f:
                my_dict = json.load(f)
            ans = []
            for j in my_dict['voltage']:
                ans.append(np.array(my_dict['voltage'][j]['drain_1'])
                           - np.array(my_dict['voltage'][j]['drain_2']))
            data[index] = np.array(ans).flatten()
            index += 1
        return (data)

    def get_name(self):
        return ("simulator")

    def setup(self):
        base_cmd = \
            'python3 simulator.py --sim mc -n 10000 -o $output_dir/result.json'
        self.cases = []
        self.size = ["2", "4", "6", "8", "10", "12", "14"]

        for i in self.size:
            self.cases.append(Simulation(root=self.input_path(
                "WL_" + i), base_command=base_cmd,
                param="\"M1,"+i + ","+i + "," + "M2"+","+i + ","+i+"\""))

    def run(self):
        self.make_output_dir()
        ans = self.get_filtered_data()
        voltage_mean = []
        voltage_std = []
        for i in ans:
            voltage_mean.append(np.average(ans[i]))
            voltage_std.append(np.std(ans[i]))

        plt.figure()
        plt.xlabel("W/L")
        plt.ylabel("Mean")
        plt.title("Mean of distribution")
        plt.plot(self.size, voltage_mean)
        plt.savefig(self.output_path("voltage_mean.png"))
        plt.close()

        plt.figure()
        plt.xlabel("W/L")
        plt.ylabel("Std")
        plt.title("Std Dev of distribution")
        plt.plot(self.size, voltage_std)
        plt.savefig(self.output_path("voltage_std.png"))
        plt.close()


if __name__ == '__main__':
    automator = Automator(
        simulation_dir='outputs',
        output_dir='manuscript/figures',
        all_problems=[Simulator]
    )
    automator.run()
