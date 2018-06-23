Utilities for comparing mortgages taking into account the interest rate, any fees or cashback, and whether you choose to add the fees to the loan or pay them up front.

See [https://github.com/MannyMoo/MortgageCalculator/blob/master/examples/compare.py](examples/compare.py) for a few usage examples.

Given the loan value $L$, the interest rate $r$, and term in months $N$, the repayments are calculated as

$$p = \frac{L r^N}{\Sigma_{i=0}^{N-1} r^i}$$.

The most useful comparison tool is the calculation of the effective rate after a given number of payments. This calculates the effective interest paid on the initial loan after a period of time factoring in any fees or cashback. If there are fees, the effective rate will always be worse than the offered rate.

In addition, the `MortgageSequence` class allows you to string together several mortgages and look at the effect of having to remortgage after your introductory rate expires or reverting to the standard variable rate. The effective rate can also be calculated on sequences of mortgages.