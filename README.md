# Bond-Portfolio-Optimization

 I think this program is useful by showing one good method that financial institutions use to mitigate net exposure to interest rate volatility. This method is to simply match the duration between assets and liabilities and then maximize convexity.

Real life examples are:

·        A bank that that has a certain funding profile with its respective weighted average duration and needs to invest in a credit and fixed income portfolios, and eventually other assets, whose weighted average duration matches the former one;

·        A pension fund that has an expected schedule payment of benefits that needs to invest in a bond portfolio that gives the income that is needed to pay those benefits, while matching the durations to avoid solvency risks.

If we focus on the pension fund, for example, the rationale would be: firstly, given the schedule of benefit payments with a duration of x and a NPV of y, what would be the ideal bond weights that we need to invest on in order to mitigate interest rate risk; and secondly, what would be the quantities on each bond that would result in the best convexity profile and thus giving the portfolio market value that would equal or surpass that NPV.

To solve the ideal bond weights part, I selected the Monte Carlo simulation because it is simple and, depending on the number of simulations, not only generates the result we are looking for but also, at the same time, gives other simulations that can satisfy other queries we would like to have.

I left comments on almost all lines of code in order to clarify things, but feel completely free to ask anything and comment. Thanks.
