from sympy import symbols, exp, sin, Eq, init_printing
from IPython.display import display

# Habilita a visualização matemática bonita
init_printing(use_unicode=True)

# 1. Definindo os símbolos
x, y, z = symbols('x y z')

# 2. Ajustando suas funções

# Exponencial: y = 1/x (Nota: se quiser e^(1/x), use exp(1/x))
exponencial_function = Eq(y, 1/x)
def exponencial_func():
	return y = 1/x

# Circunferência: x² + y² = 9
circuferencia_function = Eq(x**2 + y**2, 9)

# Módulo/Reta: y = -2x
module_function = Eq(y, -2*x)

# Duas Parábolas (Senoide): x = -3 * sin(y)
duas_parabolas_function = Eq(x, -3*sin(y))

# 3. Exibindo os resultados
print("Função Exponencial:")
display(exponencial_function)

print("Circunferência:")
display(circuferencia_function)

print("Função Linear/Módulo:")
display(module_function)

print("Duas Parábolas/Senoide:")
display(duas_parabolas_function)
