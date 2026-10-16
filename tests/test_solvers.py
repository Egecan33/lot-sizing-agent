"""Small MILP regressions; requires gurobipy, smolagents and a Gurobi license."""
import unittest
from tools.lot_sizing_tool import _solve_core
from tools.capacitated_lot_sizing_tool import _solve_cap_core


class SolverTests(unittest.TestCase):
    def check_balance_and_cost(self, result, demand, setup, unit, holding, initial=0):
        plan, inventory, flags, objective = result
        previous = initial
        for t, quantity in enumerate(plan):
            self.assertAlmostEqual(previous + quantity - demand[t], inventory[t])
            self.assertGreaterEqual(inventory[t], -1e-7)
            if quantity > 1e-7:
                self.assertEqual(flags[t], 1)
            previous = inventory[t]
        self.assertAlmostEqual(objective, setup * sum(flags) + unit * sum(plan) + holding * sum(inventory))

    def test_uncapacitated_batches_when_holding_is_cheaper(self):
        result = _solve_core([5, 5], 10, 2, 1, 0)
        self.assertEqual(result[0], [10, 0])
        self.assertAlmostEqual(result[3], 35)
        self.check_balance_and_cost(result, [5, 5], 10, 2, 1)

    def test_uncapacitated_splits_when_holding_is_expensive(self):
        result = _solve_core([5, 5], 10, 2, 10, 0)
        self.assertEqual(result[0], [5, 5])
        self.assertAlmostEqual(result[3], 40)
        self.check_balance_and_cost(result, [5, 5], 10, 2, 10)

    def test_initial_inventory(self):
        result = _solve_core([5, 5], 10, 2, 1, 5)
        self.assertEqual(result[0], [0, 5])
        self.assertAlmostEqual(result[3], 20)
        self.check_balance_and_cost(result, [5, 5], 10, 2, 1, initial=5)

    def test_capacity_forces_multiple_setups(self):
        result = _solve_cap_core([5, 5], [5, 5], 10, 2, 1, 0)
        self.assertEqual(result[0], [5, 5])
        self.assertAlmostEqual(result[3], 40)
        self.check_balance_and_cost(result, [5, 5], 10, 2, 1)
        self.assertTrue(all(p <= c + 1e-7 for p, c in zip(result[0], [5, 5])))

    def test_capacity_infeasible(self):
        with self.assertRaises(RuntimeError):
            _solve_cap_core([5, 5], [4, 5], 10, 2, 1, 0)

    def test_capacity_length_mismatch(self):
        with self.assertRaises(ValueError):
            _solve_cap_core([5, 5], [5], 10, 2, 1, 0)


if __name__ == '__main__':
    unittest.main()
