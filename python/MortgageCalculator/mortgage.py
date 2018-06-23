''' Utilities for comparing mortgages with different rates, terms, fees etc.'''


class Mortgage(object) :
    '''Basic mortgage class.'''

    __slots__ = ('housevalue', 'initloan', 'loan', 'rate', 'term', 'cashbalance', 'repayment')

    def __init__(self, housevalue, loan, rate, term, fee, cashback = 0., borrowfee = True) :
        '''housevalue : value of the house you're borrowing against in GBP (or any currency).
        loan : amount you're borrowing.
        rate : interest rate in %.
        term : term of the mortgage in years.
        fee : any fees associated with the mortgage (eg: setup fee, valuation).
        cashback : any cashback offered with the mortgage.
        borrowfee : whether to add the fees onto the loan or pay them up front.
        '''
        
        self.housevalue = housevalue
        self.rate = (rate/100. + 1.)**(1./12)
        self.term = term * 12
        self.initloan = float(loan)
        self.loan = float(loan)
        self.cashbalance = float(cashback)
        if borrowfee :
            self.loan += fee
        else :
            self.cashbalance -= fee

        self.calc_repayment()

    def calc_repayment(self) :
        '''Calculate the monthly repayment. This reproduces within < 1 % what I get 
        from online mortgage calculators. Possibly their definition of a month is 
        different. I use 1/12 of a year.'''
        
        # Would be this if the first payment comes off before interest is applied.
        # self.repayment = self.loan * self.rate ** self.term \
        #                  / sum(self.rate**n for n in xrange(1, self.term+1))

        # This if interest is applied before the first payment
        self.repayment = self.loan * self.rate ** self.term \
                         / sum(self.rate**n for n in xrange(0, self.term))

    def remaining_loan(self, npayments) :
        '''Get the remaining loan after the given number of payments. Interest is applied
        before each payment.'''
        loan = self.loan
        for i in xrange(npayments) :
            # Would be this if the first payment comes off before interest is applied.
            # loan -= self.repayment
            # loan *= self.rate

            # This if interest is applied before the first payment
            loan *= self.rate
            loan -= self.repayment
        return loan

    def effective_rate_after(self, npayments) :
        '''Get the effective interest rate after a certain number of payments
        from the initial loan value, the remaining loan, and the monthly repayment.
        This takes into account any fees and cashback, and whether you add the fees
        onto the loan or pay them up front.'''
        
        loan = self.remaining_loan(npayments) - self.cashbalance
        effectiverate = 0.1
        deltarate = 0.1
        # Iterate, incrementing the rate, til we get the correct remaining loan
        # after the given number of payments, given the initial loan (not including fees)
        # and the monthly repayment.
        while True :
            meff = Mortgage(self.housevalue, self.initloan, effectiverate, self.term, 0.)
            meff.repayment = self.repayment
            effloan = meff.remaining_loan(npayments)
            if effloan < loan :
                effectiverate += deltarate
            else :
                effectiverate -= deltarate
                deltarate /= 10.
                if deltarate == 1e-5 :
                    break
        return effectiverate

    def loan_to_value(self) :
        '''Get the loan to value at the start of the mortgage.'''
        return self.loan/self.housevalue
    
    def __str__(self) :
        '''Get a human readable string reperesentation of the mortgage.'''
        
        return '''{0:<20} : {1:.2f}
{2:<20} : {3:.2f}
{4:<20} : {5:.2f}
{6:<20} : {7:.2f}
{8:<20} : {9}
{10:<20} : {11}
{12:<20} : {13:.2f}'''.format('House value', self.housevalue,
                              'Loan', self.loan,
                              'Loan/value', self.loan_to_value()*100.,
                              'Rate [%]', (self.rate**12 - 1.)*100.,
                              'Term [years]', self.term/12.,
                              'Cash balance', self.cashbalance,
                              'Repayment', self.repayment)


    def print_summary(self, npayments = 0) :
        '''Print a summary of the mortgage at completion or after a certain
        number of payments.'''
        
        if npayments == 0 :
            npayments = self.term
        summary = str(self)
        loan = self.remaining_loan(npayments)
        effrate = self.effective_rate_after(npayments)
        summary += '\n - After ' + str(npayments) + ' payments:'
        summary += '''
{0:<20} : {1:.2f}
{2:<20} : {3:.2f}
{4:<20} : {5:.2f}
{6:<20} : {7:.2f}
{8:<20} : {9:.2f}'''.format('Remaining loan', loan,
                            'Remaining loan/initial loan', loan/self.initloan,
                            'Total paid', self.repayment * npayments,
                            'Total paid/initial loan', self.repayment * npayments / self.initloan,
                            'Effective rate [%]', effrate)
        print summary

class MortgageSequence(Mortgage) :
    '''A sequence of mortgages with different parameters.'''
    
    def __init__(self, housevalue, loan, term, mortgage1, mortgage2, *mortgages) :
        '''housevalue : value of the house you're borrowing against in GBP (or any currency).
        loan : amount you're borrowing.
        term : total term of the mortgages in years.
        
        Each mortgage should be a dict with 'rate', 'fee', and 'term' elements, and optionally 
        'cashback' and 'borrowfee' elements. The 'term' element of each mortgage should be the number
        of years that the mortgage will be used for. The term of the final mortgage
        is calculated as the total term minus the sum of terms of the preceding mortgages.'''
        
        self.housevalue = float(housevalue)
        self.term = term * 12
        self.initloan = float(loan)
        self.cashbalance = 0.
        
        self.mortgages = []
        remainingterm = self.term
        remainingloan = self.initloan
        
        for mortgageinfo in (mortgage1, mortgage2) + mortgages :
            mortgage = Mortgage(housevalue, remainingloan, mortgageinfo['rate'],
                                remainingterm/12, mortgageinfo['fee'], mortgageinfo.get('cashback', 0.),
                                mortgageinfo.get('borrowfee', True))
            self.mortgages.append([mortgageinfo['term'] * 12, mortgage])
            remainingterm -= mortgageinfo['term'] * 12
            remainingloan = mortgage.remaining_loan(mortgageinfo['term'] * 12)
            self.cashbalance += mortgage.cashbalance
            
        self.loan = self.mortgages[0][1].loan
        
        self.mortgages[-1][0] = self.term - sum(term for term, mort in self.mortgages[:-1])

        self.calc_repayment()

        self.rate = (self.effective_rate_after(self.term)/100. + 1.)**(1./12)
        
    def calc_repayment(self) :
        '''Calculate the average rate of the mortgages in the sequence, weighted
        by their terms.'''
        
        self.repayment = 0.
        for term, mortgage in self.mortgages :
            self.repayment += mortgage.repayment * term / self.term

    def remaining_loan(self, npayments) :
        '''Get the remaining loan after the given number of payments. Interest is applied
        before each payment.'''

        remainingpayments = npayments
        for term, mortgage in self.mortgages :
            if remainingpayments - term <= 0 :
                return mortgage.remaining_loan(remainingpayments)
            remainingpayments -= term

    def __str__(self) :
        '''Get a human readable string reperesentation of the mortgage sequence.'''

        selfstr = Mortgage.__str__(self)
        for i, (term, mortgage) in enumerate(self.mortgages) :
            selfstr += '\n - Mortgage ' + str(i)
            selfstr += '\n{0:<20} : {1}\n'.format('Term used', term/12.)
            mortstr = str(mortgage)
            selfstr += mortstr
        return selfstr
    
