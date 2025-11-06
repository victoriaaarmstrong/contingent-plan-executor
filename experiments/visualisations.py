import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

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

print(dynamic.describe())
print(static.describe())

none_s = static[static['condition'] == 'none']
one_s = static[static['condition'] == 'one']
two_s = static[static['condition'] == 'two']
three_s = static[static['condition'] == 'three']
none_d = dynamic[dynamic['condition'] == 'none']
one_d = dynamic[dynamic['condition'] == 'one']
two_d = dynamic[dynamic['condition'] == 'two']
three_d = dynamic[dynamic['condition'] == 'three']

"""
print("STATIC")
print("\tnone")
print(none_s['convo_length'].mean())
print(none_s['convo_length'].std())
print(none_s['number_redundant'].mode()[0])
print("\tone")
print(one_s['convo_length'].mean())
print(one_s['convo_length'].std())
print(one_s['number_redundant'].mode()[0])
print("\ttwo")
print(two_s['convo_length'].mean())
print(two_s['convo_length'].std())
print(two_s['number_redundant'].mode()[0])
print("\tthree")
print(three_s['convo_length'].mean())
print(three_s['convo_length'].std())
print(three_s['number_redundant'].mode()[0])

print("DYNAMIC")
print("\tnone")
print(none_d['convo_length'].mean())
print(none_d['convo_length'].std())
print(none_d['number_redundant'].mode()[0])
print("\tone")
print(one_d['convo_length'].mean())
print(one_d['convo_length'].std())
print(one_d['number_redundant'].mode()[0])
print("\ttwo")
print(two_d['convo_length'].mean())
print(two_d['convo_length'].std())
print(two_d['number_redundant'].mode()[0])
print("\tthree")
print(three_d['convo_length'].mean())
print(three_d['convo_length'].std())
print(three_d['number_redundant'].mode()[0])

static_no_none = no_none_df[no_none_df['mode'] == 'static']
dynamic_no_none = no_none_df[no_none_df['mode'] == 'dynamic']
"""

## No none
"""
sns.set_theme(style="darkgrid")

sns.histplot(data=static_no_none, x="number_redundant", color="skyblue", label="Static", kde=False, binwidth=0.5)
sns.histplot(data=dynamic_no_none, x="number_redundant", color="red", label="Dynamic", kde=False, binwidth=0.4)

plt.ylabel("Count")
plt.xlabel("Number of Redundant Questions")
plt.legend()

plt.savefig("./experiments/redundant_combined_hist_no_none.png", dpi=600, bbox_inches="tight")

plt.show()
"""

"""
## All on one -- This is what you want to plot!!
sns.set_theme(style="darkgrid")

#sns.histplot(data=static, x="number_redundant", color="skyblue", label="Static", kde=False, multiple='dodge')#binwidth=0.5)
#sns.histplot(data=dynamic, x="number_redundant", color="red", label="Dynamic", kde=False, multiple='dodge') #binwidth=0.4)
sns.histplot(data=no_none_df, x="number_redundant", hue="mode", multiple="dodge", palette={"static": "skyblue", "dynamic": "red"}, kde=False, binwidth=0.5)
plt.ylabel("Count")
plt.xlabel("Number of Redundant Questions")
#plt.xticks([0, 1, 2, 3, 4, 5])
plt.legend(title="", labels=["Static", "Dynamic"])

plt.savefig("./experiments/results_wout_baseline.png", dpi=600, bbox_inches="tight")

plt.show()
"""

## All on one -- Length!!
sns.set_theme(style="darkgrid")

#sns.histplot(data=static, x="number_redundant", color="skyblue", label="Static", kde=False, multiple='dodge')#binwidth=0.5)
#sns.histplot(data=dynamic, x="number_redundant", color="red", label="Dynamic", kde=False, multiple='dodge') #binwidth=0.4)
sns.histplot(data=no_none_df, x="convo_length", hue="mode", multiple="dodge", palette={"static": "skyblue", "dynamic": "red"}, kde=False, binwidth=0.5)
plt.ylabel("Count")
plt.xlabel("Conversation Length")
#plt.xticks([0, 1, 2, 3, 4, 5])
plt.legend(title="", labels=["Static", "Dynamic"])

plt.savefig("./experiments/results_length_wout_baseline.png", dpi=600, bbox_inches="tight")

plt.show()

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