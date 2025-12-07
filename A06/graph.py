import pandas as pd
import matplotlib.pyplot as plt

# Load data from CSV
data = pd.read_csv("graph.csv", sep=";")

x = data["x"]
y = data["y"]

# Create plot
plt.plot(x, y)
plt.xlabel("x")
plt.ylabel("y")
plt.title("Graph from CSV")

# Save the graph
plt.savefig("graph.png")

# Show the graph
plt.show()