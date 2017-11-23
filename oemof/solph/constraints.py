# -*- coding: utf-8 -*-

import pyomo.environ as po


def emission_limit(om, flows=None, limit=None):
    """
    Parameters
    ----------
    om : oemof.solph.Model
        Model to which constraints are added.
    flows : dict
        Dictionary holding the flows that should be considered in constraint.
        Keys are (source, target) objects of the Flow. If no dictionary is given
        all flows containing the 'emission' attribute will be used.
    limit : numeric
        Absolute emission limit.

    Note
    ----
    Flow objects required an emission attribute!

    """

    if flows is None:
        flows = {}
        for (i, o) in om.flows:
            if hasattr(om.flows[i, o], 'emission'):
                flows[(i, o)] = om.flows[i, o]

    else:
        for (i, o) in flows:
            if not hasattr(flows[i, o], 'emission'):
                raise ValueError(('Flow with source: {0} and target: {1} '
                                 'has no attribute emission.').format(i.label,
                                                                      o.label))

    def emission_rule(m):
        """
        """
        return (sum(m.flow[i, o, t] * flows[i, o].emission
                for (i, o) in flows
                for t in m.TIMESTEPS) <= limit)

    om.emission_limit = po.Constraint(rule=emission_rule)

    return om


def equate_variables(om, var1, var2, factor1=1, name=None):
    """
    Set two variables to equal adaptable by a factor.

    **The following constraints are build:**

      .. math::
        var1 \\cdot factor1 \\eq var2

    Parameters
    ----------
    name
    factor1
    var1 : po.Var
        First variable, to be set to equal with Var2 and multiplied with
        factor1.
    var2 : po.Var
        Second variable, to be set equal to (Var1 * factor1).
    factor1 : float
        Factor to define the proportion between the variables.
    name : str
        Optional name for the equation e.g. in the LP file. By default the
        name is: equate + string representation of var1 and var2.
    om : oemof.solph.Model
        Model to which constraints are added.

    Returns
    -------
    om.solph.Model

    Examples
    --------
    The following example shows how to define a transmission line in the
    investment mode by connecting both investment variables.

    >>> import pandas as pd
    >>> from oemof import solph
    >>> date_time_index = pd.date_range('1/1/2012', periods=5, freq='H')
    >>> energysystem = solph.EnergySystem(timeindex=date_time_index)
    >>> bel1 = solph.Bus(label='electricity1')
    >>> bel2 = solph.Bus(label='electricity2')
    >>> line12 = solph.Transformer(
    ...    label='powerline_1_2',
    ...    inputs={bel1: solph.Flow()},
    ...    outputs={bel2: solph.Flow(investment=solph.Investment(ep_costs=20))})
    >>> line21 = solph.Transformer(
    ...    label='powerline_2_1',
    ...    inputs={bel2: solph.Flow()},
    ...   outputs={bel1: solph.Flow(investment=solph.Investment(ep_costs=20))})
    >>> om = solph.Model(energysystem)
    >>> ## Alternatively you can find the objects by their labels.
    >>> # bel1 = energysystem.groups['electricity1']
    >>> # bel2 = energysystem.groups['electricity2']
    >>> # line12 = energysystem.groups['powerline_1_2']
    >>> # line21 = energysystem.groups['powerline_2_1']
    >>> solph.constraints.equate_variables(
    ...    om,
    ...    om.InvestmentFlow.invest[line12, bel2],
    ...    om.InvestmentFlow.invest[line21, bel1],
    ...    2)
    """
    if name is None:
        name = '_'.join(["equate", str(var1), str(var2)])

    def equate_variables_rule(m):
        return var1 * factor1 == var2
    setattr(om, name, po.Constraint(rule=equate_variables_rule))
