"""
optimizer_core.py

Core logic for defining and solving product assortment and stock optimization problems (ILP).
This module is designed to be imported by a Flask app or other interfaces.

Classes:
    OptimizationError: Custom exception for optimization-related errors.
    IntegerVariable: Class representing a product (as an optimization variable).

Functions:
    create_integer_variable: Add a product to the shared list.
    optimize: Solve the product optimization problem.
    clear_variables: Clear the products list.

@author: Mafu
@date: 2025-06-14
"""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, List, Tuple
from pulp import LpProblem, LpVariable, LpMaximize, lpSum, PULP_CBC_CMD, LpStatus

class OptimizationError(Exception):
    """Custom exception for optimization-related errors."""
    pass

@dataclass
class IntegerVariable:
    """
    Represents a product for optimization (as an integer or continuous variable).
    Uses dataclass for automatic __init__, __repr__, etc.
    """
    name: str
    lowerBound: int = 0  # Min stock/order
    upperBound: Optional[int] = None  # Max stock/order
    profit: float = 0.0  # Unit margin
    integer: bool = True  # Whole units only?
    multiplier: int = 1  # Units per package

    def to_dict(self) -> Dict:
        """Convert to a dictionary for JSON export (product-centric)."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'IntegerVariable':
        """Create a product (IntegerVariable) from a dictionary."""
        return cls(**data)

    def validate(self) -> None:
        """
        Validate the product's properties.
        Raises OptimizationError if validation fails.
        """
        if self.lowerBound < 0:
            raise OptimizationError(f"Min stock must be non-negative for {self.name}")
        if self.upperBound is not None and self.upperBound < self.lowerBound:
            raise OptimizationError(f"Max stock must be greater than min stock for {self.name}")
        if self.multiplier <= 0:
            raise OptimizationError(f"Units per package must be positive for {self.name}")

# Global products list
variables_list: List[IntegerVariable] = []

def create_integer_variable(name: str, lowerBound: int, upperBound: Optional[int],
                          profit: float, integer: bool = True, multiplier: int = 1) -> None:
    """
    Create and validate a product (IntegerVariable), then add it to the global list.
    
    Args:
        name: Product name.
        lowerBound: Min stock/order.
        upperBound: Max stock/order (None for unbounded).
        profit: Unit margin.
        integer: Whole units only?
        multiplier: Units per package.
    
    Raises:
        OptimizationError: If validation fails.
    """
    var = IntegerVariable(name=name, lowerBound=lowerBound, upperBound=upperBound,
                         profit=profit, integer=integer, multiplier=multiplier)
    var.validate()
    variables_list.append(var)

def clear_variables() -> None:
    """Clear the global products list."""
    variables_list.clear()

def optimize(variables: List[IntegerVariable], budget: float) -> Tuple[float, Dict[str, int]]:
    """
    Set up and solve the product optimization problem to maximize total margin.
    
    Args:
        variables: List of products to optimize.
        budget: Budget constraint value.
    
    Returns:
        Tuple of (max_profit, result_dict).
        max_profit is the maximum margin achieved.
        result_dict maps product names to their optimal values.
    
    Raises:
        OptimizationError: If optimization fails or produces invalid results.
    """
    if not variables:
        raise OptimizationError("No products to optimize")
    if budget <= 0:
        raise OptimizationError("Budget must be positive")

    # Create and set up the model
    model = LpProblem("Product_Stock_Optimization", LpMaximize)
    lp_vars = {}

    # Create PuLP variables (products)
    for var in variables:
        lp_vars[var.name] = LpVariable(var.name, lowBound=var.lowerBound,
                                     upBound=var.upperBound,
                                     cat='Integer' if var.integer else 'Continuous')

    # Add constraints (budget/stock constraint)
    budget_constraint = lpSum([var.multiplier * lp_vars[var.name] for var in variables])
    model += (budget_constraint <= budget, "Budget_Constraint")

    # Set objective function (maximize total margin)
    total_margin = lpSum([var.profit * var.multiplier * lp_vars[var.name] for var in variables])
    model += total_margin, "Total_Margin"

    # Solve the model
    solver = PULP_CBC_CMD(msg=False)
    model.solve(solver)

    # Check solution status
    if LpStatus[model.status] != 'Optimal':
        raise OptimizationError(f"Failed to find optimal solution: {LpStatus[model.status]}")

    # Process results
    max_margin = 0
    result = {}
    for var in variables:
        optimal_value = lp_vars[var.name].varValue
        if optimal_value is None:
            optimal_value = 0
        optimal_value = int(optimal_value)
        scaled_value = optimal_value * var.multiplier
        result[var.name] = scaled_value
        max_margin += var.profit * scaled_value

    return float(f'{max_margin:.2f}'), result
