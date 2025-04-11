import pandas as pd
df = pd.read_csv('paths.csv')
best_row = df.loc[df['reward'].idxmax()]
best_pattern = best_row['pattern'] 