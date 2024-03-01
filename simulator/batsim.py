import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


def simulate_proportional_work_cells(cell_capacities, load, charge_current, cycles, nominal_voltage=3.7, max_voltage=4.2, min_voltage=2.8):
    cells_percentage = [capacity / sum(cell_capacities) for capacity in cell_capacities]
    cells = np.array(cell_capacities, dtype=float)
    cell_voltage = np.full(len(cells), nominal_voltage)
    pack_capacity_wh_over_cycles = []
    cell_voltages_per_cycle = []  # Store cell voltages for each cycle

    for cycle in range(cycles):
        # Discharging phase
        while min(cell_voltage) > min_voltage:
            discharge_amount_wh = load * nominal_voltage / 60  # Discharge for one minute in Wh
            for i in range(len(cells)):
                cells[i] -= (discharge_amount_wh * 100 / len(cells)) / nominal_voltage
            cell_voltage = np.array([np.interp(cells[i], [0, cell_capacities[i]], [min_voltage, max_voltage]) for i in range(len(cells))])
            if min(cell_voltage) <= min_voltage:
                break

        # Charging phase
        while max(cell_voltage) < max_voltage:
            charge_amount_wh = charge_current * nominal_voltage / 60  # Charge for one minute in Wh
            for i in range(len(cells)):
                cells[i] += (charge_amount_wh * cells_percentage[i]) / nominal_voltage
            cell_voltage = np.array([np.interp(cells[i], [0, cell_capacities[i]], [min_voltage, max_voltage]) for i in range(len(cells))])
            if max(cell_voltage) >= max_voltage:
                break


        # Record pack capacity and cell voltages after each cycle
        total_pack_capacity_wh = np.sum(cells) * nominal_voltage
        pack_capacity_wh_over_cycles.append(total_pack_capacity_wh)
        cell_voltages_per_cycle.append(cell_voltage.copy())  # Record the voltages

    return {
        "final_cell_states": cells,
        "final_cell_voltages": cell_voltage,
        "cycles_completed": cycle + 1,
        "pack_capacity_wh_per_cycle": pack_capacity_wh_over_cycles,
        "cell_voltages_per_cycle": cell_voltages_per_cycle  # Return cell voltages
    }

# Example usage
cell_capacities = [280, 284, 287, 275]
load = 100
charge_current = 50
cycles = 50

result = simulate_proportional_work_cells(cell_capacities, load, charge_current, cycles)

# Plotting
plt.figure(figsize=(12, 8))

# Plot for pack capacity degradation
plt.subplot(2, 1, 1)
plt.plot(range(result['cycles_completed']), result['pack_capacity_wh_per_cycle'], marker='o')
plt.title('Pack Capacity and Cell Voltage Degradation Over Cycles')
plt.xlabel('Cycle Number')
plt.ylabel('Total Pack Capacity (Wh)')
plt.grid(True)

# Plot for cell voltage degradation
plt.subplot(2, 1, 2)
for i in range(len(cell_capacities)):
    plt.plot(range(result['cycles_completed']), [v[i] for v in result['cell_voltages_per_cycle']], marker='.', label=f'Cell {i+1} Voltage')
plt.xlabel('Cycle Number')
plt.ylabel('Cell Voltage (V)')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()
