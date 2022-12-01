# %%
import matplotlib.pyplot as plt
import pandas as pd

# %%
df = pd.read_csv("data/example_factor.csv")
# %%
df.columns
# %%
df["MKT_Index"].plot()
plt.show()
# %%
df["SMB_Index"].plot()
plt.show()
# %%
df["HML_Index"].plot()
plt.show()
# %%
df["RF_Index"].plot()
plt.show()
# %%
