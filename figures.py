# -*- coding: utf-8 -*-
"""
@author: haris
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#Set the default DPI for plots to 300
plt.rcParams["figure.dpi"] = 300

#Set the default style for Seaborn
sns.set_theme(style = "white")

#Create dataframe "pv" by calling pd.read_pickle() to read ca_csi_2020_pkl.zip
pv = pd.read_pickle("ca_csi_2020_pkl.zip")

#Call the .info() method on "pv"
print("Column name, non-null value count, and datatype per CSI application record:", pv.info())

#Set up list of categorical variables
catvars = ["app_status", "sector", "state", "inst_status", "type"]

#Quick overview of the values taken on by the categorical variables
for var in catvars:
    print(var)
    print(pv[var].value_counts())
    fig = sns.catplot(y = var, data = pv, kind = "count")

#Filter dataset down to residential projects that have been completed and are installed
res = pv.query("sector == 'Residential'")
res = res.query("app_status == 'Completed'")
res = res.query("inst_status == 'Installed'")

#Print message indicating the number of original records in "pv" and the number in "res" after filtering
print("Number of original records:", len(pv), 
      "\nNumber of records after filtering:", len(res))

#Convert the "year" column of "res" to an integer by using the .astype(int) method
res["year"] = res["year"].astype(int)

#Build a couple of additional figures showing project counts
for var in ["third_party", "year"]:
    fig = sns.catplot(y = var, data = res, kind = "count")
    fig.tight_layout()
    fig.savefig(f"res_{var}.png")
    
#Look into the nameplate capacity and cost of the systems in more detail
#Drop any records that are missing data for those specific fields
#Set "n_original" to the original length of "res"
#Set "n_now" to the new length of "res", and print informative message indicating the number of records dropped (difference between "n_original" and "n_now")
n_original = len(res)
res = res.dropna(subset=["nameplate", "total_cost"])
n_now = len(res)
print("Number of dropped records with missing data for nameplate capacity and total cost:", n_original - n_now)

#Create a figure with two panels in a row, a meaningless histogram skewed by a few projects in the dataset with much larger capacities or costs than normal for residential projects
#Set "fig, (ax1, ax2)" to the result of calling plt.subplots(1, 2), where the arguments 1 and 2 in the call indicate the number of rows and columns of panels in the plot
#Call .plot.hist() on the "nameplate" column of "res" with the argument "ax = ax1" to put the histogram in the left panel
#Set titles for both panels, and tighten the figure's layout
fig, (ax1, ax2) = plt.subplots(1, 2)
res["nameplate"].plot.hist(ax = ax1)    
ax1.set_title("Nameplate")
res["total_cost"].plot.hist(ax = ax2)
ax2.set_title("Cost")
fig.tight_layout()

#Remove the projects above the 99th percentile in size or cost
#Set "kw99" equal to the result of calling .quantile(0.99) on the "nameplate" column of "res", which will pick out the nameplate capacity at the 99th percentile
#Similarly, set "tc99" equal to 99th percentile of the "total_cost" column of "res", and print informative message about both "kw99" and "tc99"
kw99 = res["nameplate"].quantile(0.99)
tc99 = res["total_cost"].quantile(0.99)
print("Completed CSI projects at or below the 99th percentile in total cost:", tc99)
print("Completed CSI projects at or below the 99th percentile in size:", kw99)

#Create new dataframe "trim" by calling the .query() method on "res" with the argument "f'nameplate <= {kw99} and total_cost <= {tc99}'"
#Print new number of records in "trim" to make sure a reasonable number (between 1 and 2 percent) were removed
trim = res.query(f"nameplate <= {kw99} and total_cost <= {tc99}")
print("Number of CSI project records at or below the 99th percentile in total cost or size:", len(trim))

#Construct a similar two-panel figure for the "trim" dataframe
#Save the figure as "res_nameplate_cost.png"
fig, (ax1, ax2) = plt.subplots(1, 2)
trim["nameplate"].plot.hist(ax = ax1)    
ax1.set_title("Nameplate")
trim["total_cost"].plot.hist(ax = ax2)
ax2.set_title("Cost")
fig.tight_layout()
fig.savefig(f"nameplate_cost.png")

#Use Seaborn to do some comparisons of projects with different values of the "third_party" variable
#Use "var" to loop over a list consisting of the column names "nameplate" and "total_cost"
#Create a new (single-panel) figure with an established 300 DPI resolution by setting "fig, ax1" equal to the result of calling plt.subplots()
#Call sns.histplot() while including the arguments "hue = 'third_party'" (which causes superimposed histograms to be drawn for different values of "third_party") and "kde = True" (causes a kernel density estimate of the distribution to be added to the plot)
for var in ["nameplate", "total_cost"]:
    fig, ax1 = plt.subplots()
    sns.histplot(data = trim, x = var, hue = "third_party", kde = True, ax = ax1)
    fig.tight_layout()
    fig.savefig(f"res_{var}.png")

#Look at the distributions via boxen plots, which are a much-enhanced version of box plots
fig, ax1 = plt.subplots()
sns.boxenplot(data = trim, x = "third_party", y = "nameplate", ax = ax1)
ax1.set_title("Nameplate Capacity")
ax1.set_xlabel("Third Party")
ax1.set_ylabel("kW")
fig.tight_layout()
fig.savefig("res_boxen_all.png")

#Look at the distributions via violin plots, which show kernel density estimates
fig, ax1 = plt.subplots()
sns.violinplot(data = trim, x = "nameplate", y = "inst_status", hue = "third_party", split = True, ax = ax1)
ax1.set_title("Nameplate Capacity")
ax1.set_xlabel("kW")
ax1.set_ylabel("")
fig.tight_layout()
fig.savefig("res_violin.png")

#Overlay the density estimates in a single figure
fig, ax1 = plt.subplots()
sns.kdeplot(data = trim, x = "nameplate", hue = "third_party", palette = "crest", fill = True, ax = ax1)
ax1.set_title("Nameplate Capacity")
ax1.set_xlabel("kW")
ax1.set_ylabel("")
fig.tight_layout()
fig.savefig("res_kde.png")

#Look in more detail at projects by year
#Trim off the last few years (when the program was essentially over) by setting "main" equal to the result of calling .query() on "trim" with the argument "year <= 2016"
#Create a new single-panel figure, and then call sns.boxenplot() while including the "orient = 'h'" argument (which causes boxes to be drawn horizontally)
main = trim.query("year <= 2016")
fig, ax1 = plt.subplots()
sns.boxenplot(data = main, y = "year", x = "nameplate", orient = "h", ax = ax1)
ax1.set_title("Nameplate Capacity by Year")
ax1.set_xlabel("kW")
ax1.set_ylabel("Year")
fig.tight_layout()
fig.savefig("res_boxen_year.png")

#Show the joint distribution of "nameplate" and "total_cost" using a hex plot (which shows the density of points using colors that vary in intensity, and is essentially an enhanced scatter plot for large datasets)
#Produce a high-level seaborn JointGrid graphics object by first setting "jg" equal to the result of calling sns.jointplot() with arguments "data = trim", "x = 'nameplate'", "y = 'total_cost'", and "kind = 'hex'"
#Set the labels of the X and Y axes by calling the .set_axis_labels() method of "jg" with respective arguments "Nameplate" and "Total Cost"
#Set the overall title by calling jg.fig.suptitle()
# Tidy up the layout by calling jg.fig.tight_layout(), and save the figure
jg = sns.jointplot(data = trim, x = "nameplate", y = "total_cost", kind = "hex")
jg.set_axis_labels("Nameplate", "Total Cost")
jg.fig.suptitle("Distribution of Systems by Cost and Capacity") 
jg.fig.tight_layout()
jg.savefig("res_hexbin.png")