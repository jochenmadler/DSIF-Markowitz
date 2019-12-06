from abc import ABC


class Broker(ABC):
    name = None
    fixed_cost = None
    variable_cost = None


class testBroker(Broker):
    name = "testBroker"
    fixed_cost = 10
    variable_cost = 0.03
