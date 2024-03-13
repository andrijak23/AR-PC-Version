import pickle
fajl = "dist"

# Load the data from the .pkl file
with open(f'{fajl}.pkl', 'rb') as file:
    data = pickle.load(file)

# Write the data to a .txt file
with open(f'{fajl}.txt', 'w') as file:
    file.write(str(data))