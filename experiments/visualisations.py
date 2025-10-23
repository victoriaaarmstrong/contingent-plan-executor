import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

df = pd.read_csv('./experiments/results-all.csv')

bank_df = df[df['domain'] == 'bank']
gold_standard = df[df['domain'] == 'gold']

bank_df_static = bank_df[bank_df['mode'] == 'static']
bank_df_dynamic = bank_df[bank_df['mode'] == 'dynamic']
gold_standard_static = gold_standard[gold_standard['mode'] == 'static']
gold_standard_dynamic = gold_standard[gold_standard['mode'] == 'dynamic']

static = df[df['mode'] == 'static']
dynamic = df[df['mode'] == 'dynamic']


## All on one
"""
sns.set_theme(style="darkgrid")

sns.histplot(data=static, x="number_redundant", color="skyblue", label="Static", kde=True)
sns.histplot(data=dynamic, x="number_redundant", color="red", label="Dynamic", kde=True)

plt.ylabel("Count")
plt.xlabel("Number of Redundant Questions")
plt.legend()

plt.savefig("./experiments/redundant_combined_hist.png", dpi=600, bbox_inches="tight")

plt.show()
"""

## By domain
sns.set_theme(style="darkgrid")

#sns.histplot(data=bank_df_static, x="number_redundant", color="skyblue", label="Static", kde=True)
#sns.histplot(data=bank_df_dynamic, x="number_redundant", color="red", label="Dynamic", kde=True)
sns.histplot(data=gold_standard_static, x="number_redundant", color="skyblue", label="Static", kde=True)
sns.histplot(data=gold_standard_dynamic, x="number_redundant", color="red", label="Dynamic", kde=True)

plt.ylabel("Count")
plt.xlabel("Number of Redundant Questions")
plt.legend()

plt.savefig("./experiments/redundant_gold_hist.png", dpi=600, bbox_inches="tight")

plt.show()
