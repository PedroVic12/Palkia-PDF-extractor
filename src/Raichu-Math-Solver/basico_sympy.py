from sympy import symbols, exp, init_printing
from IPython.display import display
import pandas as pd

data = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
display(data)


# Optional: Enable pretty printing (useful for non-interactive scripts)
init_printing(use_unicode=True) 

# Define the symbols
x, y, z = symbols('x y z')

# Create the expression
expr = exp(-(x**2 + y**2 + z**2))

# Display the expression
display(expr)
