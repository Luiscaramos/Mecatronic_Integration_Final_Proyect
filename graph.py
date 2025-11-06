import pandas as pd
import matplotlib.pyplot as plt

def plot_window(csv_file):
    # Load the CSV
    df = pd.read_csv(csv_file)

    if 'AnalogValue' not in df.columns:
        print("CSV must have an 'AnalogValue' column.")
        return

    total_samples = len(df)
    print(f"Total samples in file: {total_samples}")

    # Ask user for window range
    try:
        start = int(input(f"Enter start sample (0 to {total_samples - 1}): "))
        end = int(input(f"Enter end sample ({start + 1} to {total_samples}): "))
    except ValueError:
        print("Invalid input. Please enter integer values.")
        return

    if start < 0 or end > total_samples or start >= end:
        print("Invalid range. Please try again.")
        return

    # Slice the DataFrame
    data_window = df['AnalogValue'][start:end]

    # Plot
    plt.figure(figsize=(10, 4))
    plt.plot(range(start, end), data_window, label='Analog Value')
    plt.title(f"Analog Data from Sample {start} to {end}")
    plt.xlabel("Sample Number")
    plt.ylabel("Analog Value")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_window("analog_readings_20.csv")  # Change to your CSV filename if needed
