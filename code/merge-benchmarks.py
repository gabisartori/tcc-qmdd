import os
import pandas as pd

csvs = os.listdir("results")


consolidate = open("results.csv", "w")
consolidate.write("date,simulator,algorithm,n_qubits,command,mean,stddev,median,user,system,min,max\n")

for csv in csvs:
  if not csv.endswith(".csv"): continue
  *date, simulator, algorithm, n = csv.rstrip(".csv").split("-")
  date = "-".join(date)
  f = open("results/" + csv, "r")
  if len(lines := f.readlines()) < 2: continue
  consolidate.write(f"{date},{simulator},{algorithm},{n},{lines[1]}")
  f.close()

consolidate.close()


df = pd.read_csv("results.csv")

df.index = pd.to_datetime(df["date"], format="%Y-%m-%dT%H:%M:%S")
df.sort_index(inplace=True)

df.to_csv("results-sorted.csv", index=False)
