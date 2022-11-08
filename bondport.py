import pandas as pd
import numpy as np
from datetime import date, datetime

# To start the program runing time clock
start_time = datetime.now()

dfbondport = pd.read_excel("bondport.xlsx")

today = date.today()

dfbondport["price"] = dfbondport["price%"] * dfbondport["par"]
dfbondport["coupon"] = dfbondport["coupon%"] * dfbondport["par"]
dfbondport["n"] = (pd.to_datetime(dfbondport["maturity"]) - pd.to_datetime(today)).dt.days / 365 * dfbondport["freq"] #Number of coupons left until maturity
dfbondport["#ofdaysPassed"] = pd.to_datetime(today) - pd.to_datetime(dfbondport["lastcoupon"])
dfbondport["ytm"] = ((dfbondport["coupon"] + (dfbondport["par"] - dfbondport["price"]) / dfbondport["n"])) / ((dfbondport["par"] + dfbondport["price"]) / 2)


# Variables for duration calculation
y = dfbondport["ytm"] / dfbondport["freq"]
f = dfbondport["freq"]
n = dfbondport["n"]
c = dfbondport["coupon%"] / dfbondport["freq"]

dfbondport["macdur"] = ((1 + y) / (f * y)) - ((1 + y + n * (c - y)) / ((f * c * ((1 + y) ** n - 1)) + (f * y))) # Formula for macaulay duration
dfbondport["moddur"] = dfbondport["macdur"] / (1 + y) # Formula for modified duration


# Variables for convexity calculation
a = dfbondport["#ofdaysPassed"].dt.days / 365 # To convert timedelta into integer
t = n / f # Number of years left
q = (1 + dfbondport["ytm"]) # Discount factor
cp = dfbondport["coupon"]
g = (a - t) * (a - t - 1) * q ** (- 2) # Gamma

# Revised Closed-Form Solution for Bond Convexity: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3176015
dfbondport["convexity"] = (cp * (((a * (a - 1)) / q ** 2) - g + ((- a + (a - t) * q ** ( - t)) / (0.5 * dfbondport["ytm"] * q)) + ((1 - q ** ( - t)) / (0.5 * dfbondport["ytm"] ** 2))) / (dfbondport["ytm"] * dfbondport["price"])) + g


# To declare the same initial weight for all bonds
init_weight = 1 / len(dfbondport["moddur"])
weights = [init_weight for i in range(len(dfbondport["moddur"]))]

dfbondport["bondvalue"] = weights * dfbondport["price"] * len(dfbondport["moddur"]) # To get the bond value right we need to multiply again by the number of bonds in the portfolio
dfbondport["income"] = weights * dfbondport["coupon"] * len(dfbondport["moddur"]) # To get the income right we need to multiply again by the number of bonds in the portfolio

print('\n\n\n',dfbondport,'\n\n\n')
print("Total portfolio market value is: €" + str(dfbondport["bondvalue"].sum()))
print("Total income is: €" + str(dfbondport["income"].sum()))


# To calculate portfolio weighted average duration
product_for_sum_moddur = []
for i in range(0, len(dfbondport["moddur"])): # Until the number of bonds in the portfolio
	product_for_sum_moddur.append(dfbondport["moddur"][i] * dfbondport["bondvalue"][i]) # For loop that simulates Excel's sumproduct formula for the number of bonds in portfolio
sumproduct_moddur = sum(product_for_sum_moddur)
print("Portfolio weighted average duration is: " + str(np.round(sumproduct_moddur / dfbondport["bondvalue"].sum(), 3)))


# To calculate portfolio weighted average convexity in the same manner as above
product_for_sum_conv = []
for i in range(0, len(dfbondport["convexity"])):
	product_for_sum_conv.append(dfbondport["convexity"][i] * dfbondport["bondvalue"][i])
sumproduct_conv = sum(product_for_sum_conv)
print("Portfolio weighted average convexity is: " + str(np.round(sumproduct_conv / dfbondport["bondvalue"].sum(), 3)))


# Monte Carlo simulations
print("\n\n**MONTE CARLO SIMULATION**\n")

mc_sims = 10000

# To define a new dataframe containing the monte carlo simulations
mc_sims_df = pd.DataFrame(columns = ["port_val_wei_dur", "port_val_wei_conv", "weights", "port_bond_value"])

# A for loop generating mc_sims of random combinations of weights
for i in range(mc_sims):
	n_weights = np.random.random(len(dfbondport["moddur"])) # To declare random weights for each bond to use on bond value column
	n_weights /= np.sum(n_weights) # The operator "/=" is short to calculate proportions, ie, "x=x/n". This operator naturaly calculates proportions to sum 100%

	n_bondvalue = n_weights * dfbondport["price"] * len(dfbondport["moddur"]) # To get the bond value right we need to multiply again by the number of bonds in the portfolio

	product_for_sum_moddur = []
	for i in range(0, len(dfbondport["moddur"])):
		product_for_sum_moddur.append(dfbondport["moddur"][i] * n_bondvalue[i])
	sumproduct_moddur = sum(product_for_sum_moddur)
	port_val_wei_dur = np.round(sumproduct_moddur / n_bondvalue.sum(), 3)

	product_for_sum_conv = []
	for i in range(0, len(dfbondport["convexity"])):
		product_for_sum_conv.append(dfbondport["convexity"][i] * n_bondvalue[i])
	sumproduct_conv = sum(product_for_sum_conv)
	port_val_wei_conv = np.round(sumproduct_conv / n_bondvalue.sum(), 3)


	# To populate the 4 columns of the dataframe defined on code line 74
	mc_sims_df = mc_sims_df.append({"port_val_wei_dur": port_val_wei_dur, "port_val_wei_conv": port_val_wei_conv, "weights": np.round(n_weights, 3), "port_bond_value": np.round(n_bondvalue.sum(), 3)}, ignore_index=True)


# Let's assume that the weighted average duration on the liabilities side is 5.5
# In order to mitigate solvency issues, we need to match the duration between assets and liabilities
liab_dur = 5.5
delta = 0.01

# To add a column, to serve as condition, to the dataframe checking if the portfolio weighted average duration is equal to the liabilities duration and if so says TRUE.
# If it is not equal to the liabilities duration, then it check if the portfolio weighted average duration sits between a delta of 0.01 and if so it still says TRUE. Otherwise sais FALSE.
mc_sims_df["dur_match"] = np.where((mc_sims_df.port_val_wei_dur == liab_dur) | (mc_sims_df.port_val_wei_dur > (liab_dur - delta)) & (mc_sims_df.port_val_wei_dur < (liab_dur + delta)), True, False)
print(mc_sims_df)


# To filter only the simulations that match the duration of the liabilities
mc_sims_filter_df = mc_sims_df.loc[(mc_sims_df["dur_match"] == True)]
print(mc_sims_filter_df)


# To grab the row which has the maximum portfolio bond value
max_port_value = mc_sims_filter_df.loc[mc_sims_filter_df["port_val_wei_conv"].idxmax()]


print("\n**MAXIMUM PORTFOLIO WEIGHTED AVERAGE CONVEXITY**\n")
print(max_port_value)


# To end the program runing time clock
end_time = datetime.now()
print("\n\nTime spent: {}".format(end_time - start_time))


with pd.ExcelWriter("output_bondport.xlsx") as writer:
	dfbondport.to_excel(writer, sheet_name = "bond portfolio")
	mc_sims_df.to_excel(writer, sheet_name = "all MC simulations")
	mc_sims_filter_df.to_excel(writer, sheet_name = "filtered MC simulations")
	max_port_value.to_excel(writer, sheet_name = "chosen weights")
