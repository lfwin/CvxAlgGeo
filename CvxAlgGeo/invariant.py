#******************************************************************************#
#       Copyright (C) 2011-2013 Mehdi Ghasemi <mehdi.ghasemi@usask.ca>         #
#                                                                              #
#  Distributed under the terms of the GNU General Public License (GPL)         #
#  as published by the Free Software Foundation; either version 2 of           #
#  the License, or (at your option) any later version                          #
#                  http://www.gnu.org/licenses/                                #
#******************************************************************************#

from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
from sage.rings.rational_field import *
from sage.groups.perm_gps.permgroup_named import *
class InvariantPolynomial:
    """
    A class for computations on polynomials invariant under a finite group of permutations.
    """
    MainPolynomial = 0
    Ring = []
    NumVars = 1
    vars = []
    Grp = []
    Omega = []
    QuotientOmega = []
    MinimalOmega = []
    Poly_max = 0
    
    
    def __init__(self, Prg, Rng, Settings = {}):
        
        self.MainPolynomial = Prg[0]
        self.Ring = Rng
        self.vars = self.Ring.gens()
        self.NumVars = len(self.vars)
        ###
        f_tot_deg = self.MainPolynomial.total_degree()
        if len(Prg) > 1:
            self.Grp = Prg[1]
        else:
            self.Grp = SymmetricGroup(self.NumVars)
        self.Omega = self.MainPolynomial.exponents()
        self.MainPolynomial = self.Reynolds(Prg[0], self.Grp)
    
    def SigmaAlpha(self, sigma, alpha):
        """
        Takes a permutation and an n-tuple and returns the result of the permutation 
        on the indices of the tuple.
        """
        mp = sigma.dict()
        n = self.NumVars
        beta = [0 for i in range(n)]
        for i in range(n):
            beta[mp[i + 1] - 1] = alpha[i]
        return beta
        
    def GenMon(self, alpha):
        """
        Returns the monomial corresponding to the input tuple.
        """
        t = 1
        for i in range(self.NumVars):
            t = t*self.vars[i]**alpha[i]
        return t
    
    def Reynolds(self, f, G):
        """
        Computes the Reynolds operator associated o the group G on the polynomial f.
        """
        TmpPoly = 0
        n = self.NumVars
        expos = f.exponents()
        coefs = f.coefficients()
        for i in range(len(expos)):
            expo = expos[i]
            coef = coefs[i]
            for p in G.list():
                mono = self.GenMon(self.SigmaAlpha(p, expo))
                TmpPoly += coef*mono
        return (1/G.order())*TmpPoly
    
    def QOmega(self):
        """
        Finds the equivalence classes of exponents with respect to the group action.
        """
        TmpOmega = [list(alpha) for alpha in self.Omega]
        QO = []
        while TmpOmega != []:
            alpha = TmpOmega[0]
            tmpClass = []
            for p in self.Grp:
                sa = self.SigmaAlpha(p,alpha)
                if sa in TmpOmega:
                     TmpOmega.remove(sa)
                if sa not in tmpClass:
                    tmpClass.append(sa)
            QO.append(tmpClass)
        self.QuotientOmega = QO
    
    def OmegaFtilde(self):
        """
        Finds the equivalence classes of exponents of the polynomial.
        """
        tmp = []
        for cls in self.QuotientOmega:
            tmp.append(max(cls))
        self.MinimalOmega = tmp
    
    def Stabilizer(self, G, alpha):
        """
        Returns the stabilizer group of an exponent.
        """
        st = []
        for p in G.list():
            beta = self.SigmaAlpha(p,alpha)
            if alpha == beta:
                st.append(p)
        return G.subgroup(st)
    
    def tildemax(self):
        r"""
        Computes the \tilde{f}_{\max} corresponding to the polynomial and the group action.
        """
        ftilde = 0
        self.QOmega()
        self.OmegaFtilde()
        for alpha in self.MinimalOmega:
            mon = self.GenMon(alpha)
            falpha = self.MainPolynomial.coefficient(alpha)
            StIdx = self.Grp.order()/self.Stabilizer(self.Grp, alpha).order()
            ftilde = ftilde + falpha*StIdx*mon
        self.Poly_max = ftilde
        return ftilde
    
    def StblTldMax(self):
        r"""
        Finds the largest subgroup which fixes the associated ring of \tilde{f}_{\max}
        """
        ReducedVars = self.Poly_max.variables()
        TplRptVars = []
        for x in ReducedVars:
            y = [0 for i in range(self.NumVars)]
            y[self.vars.index(x)] = 1
            TplRptVars.append(y)
        Hf = []
        for p in self.Grp.list():
            flag = 1
            for v in TplRptVars:
                if self.SigmaAlpha(p,v) not in TplRptVars:
                    flag = 0
                    break
            if flag == 1:
                Hf.append(p)
        HG = self.Grp.subgroup(Hf)
        return HG
    
    def ConjugateClosure(self, H):
        G = self.Grp
        NG = G.normal_subgroups()
        Cover = []
        for K in NG:
            if H.is_subgroup(K):
                Cover.append(K)
        K = Cover[0]
        for L in Cover:
            K = K.intersection(L)
        return K
    
    def RedPart(self, f, P):
        
        g = 0
        coef = f.coefficients()
        mono = f.monomials()
        num1 = len(coef)
        num2 = len(P)
        for i in range(num1):
            t = 1
            exp = mono[i].exponents()[0]
            for j in range(self.NumVars):
                for k in range(num2):
                    if j in P[k]:
                        t = t*self.vars[k]**(exp[j])
                        break
            g = g + coef[i]*t
        return g
