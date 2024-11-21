import numpy as np
import tkinter as tk
from tkinter import filedialog
import os
from edfio import Edf, EdfSignal

def select_file():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(title="Select CSV file", filetypes=[("CSV files", "*.csv")])

def read_muse_csv(filepath):
    data_dict = {
        'TP9': [], 'AF7': [], 'AF8': [], 'TP10': []
    }
    
    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) >= 6 and '/muse/eeg' in parts[1]:
                eeg_values = [float(val) for val in parts[2:6]]
                if all(not np.isnan(v) for v in eeg_values):
                    data_dict['TP9'].append(eeg_values[0])
                    data_dict['AF7'].append(eeg_values[1])
                    data_dict['AF8'].append(eeg_values[2])
                    data_dict['TP10'].append(eeg_values[3])

    # Convert to arrays and adjust length to be divisible by data record size
    signals = []
    sf = 256  # sampling frequency
    record_size = sf  # 1-second records
    
    for ch in ['TP9', 'AF7', 'AF8', 'TP10']:
        if data_dict[ch]:
            data = np.array(data_dict[ch])
            # Trim to multiple of record size
            trim_size = len(data) - (len(data) % record_size)
            data = data[:trim_size]
            
            signals.append(EdfSignal(
                data,
                sampling_frequency=sf,
                label=ch
            ))
    
    return signals

def main():
    csv_file = select_file()
    if not csv_file:
        print("No file selected. Exiting.")
        return

    print("Reading CSV...")
    signals = read_muse_csv(csv_file)
    
    output_file = os.path.splitext(csv_file)[0] + ".edf"
    print("Converting to EDF...")
    
    edf = Edf(signals)
    edf.write(output_file)
    
    print(f"\nConverted {csv_file} to {output_file}")

if __name__ == "__main__":
    main()