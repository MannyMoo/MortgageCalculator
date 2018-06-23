#!/usr/bin/env python

from MortgageCalculator import Mortgage, MortgageSequence

value = 150000
loan = 125000
term = 25

# 2 year fix rate.
m = Mortgage(value, loan, 1.69, term, 995., borrowfee = True)
m.print_summary(24)
print

# 5 year fix rate
m = Mortgage(value, loan, 2.29, term, 995., borrowfee = True)
m.print_summary(60)
print

# 10 year fix rate
m = Mortgage(value, loan, 3.24, term, 995., borrowfee = True)
m.print_summary(60)
print

# 2 year fix then std rate.
m = MortgageSequence(value, loan, term, {'rate' : 1.69, 'fee' : 995, 'term' : 2},
                     {'rate' : 3.99, 'fee' : 0., 'term' : 16})
m.print_summary(60)
print

# Repeated remortgage for 2 years.
m = MortgageSequence(value, loan, term,
                     {'rate' : 1.69, 'fee' : 995, 'term' : 2},
                     {'rate' : 1.69, 'fee' : 995, 'term' : 2},
                     {'rate' : 1.69, 'fee' : 995, 'term' : 2})
m.print_summary(60)
print

m.print_summary()
