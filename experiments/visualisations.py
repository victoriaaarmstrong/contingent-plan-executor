import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

df = pd.read_csv('./experiments/results-all.csv')

no_none_df = df[df['condition'] != 'none']
bank_df = df[df['domain'] == 'bank']
gold_standard = df[df['domain'] == 'gold']

bank_df_static = bank_df[bank_df['mode'] == 'static']
bank_df_dynamic = bank_df[bank_df['mode'] == 'dynamic']
gold_standard_static = gold_standard[gold_standard['mode'] == 'static']
gold_standard_dynamic = gold_standard[gold_standard['mode'] == 'dynamic']

static = df[df['mode'] == 'static']
dynamic = df[df['mode'] == 'dynamic']

static_no_none = no_none_df[no_none_df['mode'] == 'static']
dynamic_no_none = no_none_df[no_none_df['mode'] == 'dynamic']

## No none
"""
sns.set_theme(style="darkgrid")

sns.histplot(data=static_no_none, x="number_redundant", color="skyblue", label="Static", kde=True)
sns.histplot(data=dynamic_no_none, x="number_redundant", color="red", label="Dynamic", kde=True)

plt.ylabel("Count")
plt.xlabel("Number of Redundant Questions")
plt.legend()

plt.savefig("./experiments/redundant_combined_hist_no_none.png", dpi=600, bbox_inches="tight")

plt.show()
"""

## All on one
# remove kde
# make columns the same size
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
"""
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
"""