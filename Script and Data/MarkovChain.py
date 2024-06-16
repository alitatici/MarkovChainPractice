import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Read the data into a pandas DataFrame
df = pd.read_csv('data.csv')

# Combine the Date and Time columns into a single datetime column
df['Datetime'] = pd.to_datetime(df['Date'], format='%d/%m/%Y %H:%M:%S')

# Extract the month and year for grouping
df['Month'] = df['Datetime'].dt.to_period('M')

# Define the state intervals
state_intervals = [(i, i+1) for i in range(1, 10)]  # Intervals from 1 to 9

# Function to group values based on intervals
def group_magnitude(magnitude):
    for interval in state_intervals:
        if interval[0] <= magnitude < interval[1]:
            return sum(interval) / 2  # Return the midpoint of the interval
    return None  # Return None if magnitude is out of defined intervals

# Apply grouping function to the Magnitude column
df['Grouped_Magnitude'] = df['Magnitude'].apply(group_magnitude)

# Drop any rows where grouping function returned None
df = df.dropna()

# Group by the month and find the maximum magnitude in each month
max_grouped_magnitude_per_month = df.groupby('Month')['Grouped_Magnitude'].max()

# Plotting the maximum grouped magnitude values over time
plt.figure(figsize=(10, 6))
plt.scatter(max_grouped_magnitude_per_month.index.to_timestamp(), max_grouped_magnitude_per_month.values)
plt.title('Maximum Grouped Magnitude of Earthquakes Over Time')
plt.xlabel('Date')
plt.ylabel('Maximum Grouped Magnitude')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

# Show plot
plt.show()

# Convert data to pandas Series
series = pd.Series(max_grouped_magnitude_per_month)

# Define the states (unique earthquake magnitudes)
states = sorted(series.unique())

transition_matrix = pd.DataFrame(0, index=states, columns=states, dtype=float)

# Iterate over the series to calculate transition counts
for i in range(len(series) - 1):
    current_state = series.iloc[i]
    next_state = series.iloc[i + 1]
    transition_matrix.loc[current_state, next_state] += 1

# Convert transition counts to probabilities
transition_matrix = transition_matrix.div(transition_matrix.sum(axis=1), axis=0)

print("Transition Matrix:")
print(transition_matrix)

P = transition_matrix.values

A = P.T - np.eye(4)

# Add the constraint that the sum of the steady-state probabilities is 1
A = np.vstack([A, np.ones(4)])

# Create the right-hand side of the equation
b = np.zeros(4)
b = np.append(b, 1)

# Solve the linear system
pi = np.linalg.lstsq(A, b, rcond=None)[0]

print("Steady-state probabilities:", pi)

mean_passage_time_months = 1/pi
print("Mean passage time (months):", mean_passage_time_months)
