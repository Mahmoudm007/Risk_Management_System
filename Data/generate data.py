import pandas as pd
import numpy as np

# Generate additional synthetic data for components
np.random.seed(1)
new_data = {
    'Component': ['NewComp' + str(i) for i in range(1, 2)],
    'Length': np.random.uniform(5, 200, 1),
    'Width': np.random.uniform(5, 200, 1),
    'Height': np.random.uniform(5, 200, 1),
    'Edges': np.random.randint(0, 6, 1),
    'Colors': np.random.choice(['Red', 'Green', 'Blue', 'Black', 'White'], 1),
    'Material': np.random.choice(['Plastic', 'Metal', 'Ceramic', 'Composite'], 1),
    'Elasticity': np.random.choice(['Low', 'Medium', 'High'], 1),
    'Connection': np.random.choice(['Wired', 'Wireless'], 1),
    'Cost (USD)': np.random.uniform(5, 1000, 1)
}

new_df = pd.DataFrame(new_data)
new_df.to_csv('new_component_data.csv', index=False)
