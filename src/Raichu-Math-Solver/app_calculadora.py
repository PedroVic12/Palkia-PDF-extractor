
# pip install PySide6 numpy sympy matplotlib rich


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculadora Científica Avançada com PySide6, SymPy e Julia
Arquitetura MVC com console CLI integrado, visualização 2D/3D, EDOs e Matrizes
Versão 3.0 - Completa
"""

import sys
import os
import json
import subprocess
import numpy as np
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTextEdit, QLineEdit, QPushButton, QLabel,
    QComboBox, QSpinBox, QDoubleSpinBox, QGroupBox, QFormLayout,
    QSplitter, QFileDialog, QMessageBox, QGridLayout, QCheckBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QInputDialog
)
from PySide6.QtCore import Qt, Signal, QObject, QThread, QProcess
from PySide6.QtGui import QFont, QTextCursor, QColor, QPalette

import sympy as sp
from sympy import (
    symbols, sin, cos, tan, exp, log, sqrt, pi, 
    diff, integrate, Matrix, solve, dsolve, Function,
    Eq, Derivative, sympify, latex, simplify, expand, factor,
    pretty, init_printing
)
from sympy.vector import CoordSys3D

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D

# Rich para formatação de console
try:
    from rich.console import Console
    from rich.syntax import Syntax
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


# ============================================================================
# MODEL - Lógica de Negócio
# ============================================================================

class FunctionModel(QObject):
    """Modelo para gerenciar funções matemáticas"""
    
    function_updated = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.x, self.y, self.z, self.t = symbols('x y z t')
        self.current_function = None
        self.function_str = ""
        self.variables = [self.x, self.y, self.z, self.t]
        self.saved_functions = {}
        self.save_file = os.path.expanduser("~/.calculadora_funcoes.json")
        self.load_from_disk()
        
    def set_function(self, expression_str: str):
        """Define a função matemática"""
        try:
            self.function_str = expression_str
            # Converte string para expressão SymPy
            self.current_function = sp.sympify(expression_str, locals={
                'x': self.x, 'y': self.y, 'z': self.z, 't': self.t,
                'sin': sin, 'cos': cos, 'tan': tan,
                'exp': exp, 'log': log, 'sqrt': sqrt, 'pi': pi
            })
            self.function_updated.emit(str(self.current_function))
            return True, f"Função definida: {self.current_function}"
        except Exception as e:
            return False, f"Erro ao definir função: {str(e)}"
    
    def evaluate(self, **kwargs):
        """Avalia a função em pontos específicos"""
        if self.current_function is None:
            return None
        try:
            subs_list = [(getattr(self, k), v) for k, v in kwargs.items() 
                         if hasattr(self, k)]
            result = self.current_function.subs(subs_list)
            return complex(result).real if result.is_real else complex(result)
        except:
            return None
    
    def get_numpy_function(self):
        """Retorna função numpy para plotagem"""
        if self.current_function is None:
            return None
        return sp.lambdify((self.x, self.y, self.z), self.current_function, 'numpy')
    
    def save_function(self, name: str):
        """Salva função no dicionário"""
        if self.current_function is None:
            return False, "Nenhuma função definida"
        self.saved_functions[name] = {
            'expression': str(self.current_function),
            'timestamp': datetime.now().isoformat()
        }
        self.save_to_disk()  # Auto-save
        return True, f"Função '{name}' salva com sucesso!"
    
    def load_function(self, name: str):
        """Carrega função salva"""
        if name not in self.saved_functions:
            return False, f"Função '{name}' não encontrada"
        expr = self.saved_functions[name]['expression']
        return self.set_function(expr)
    
    def save_to_disk(self):
        """Salva funções em arquivo JSON persistente"""
        try:
            with open(self.save_file, 'w') as f:
                json.dump(self.saved_functions, f, indent=2)
            return True
        except Exception as e:
            print(f"Erro ao salvar: {e}")
            return False
    
    def load_from_disk(self):
        """Carrega funções do arquivo JSON"""
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r') as f:
                    self.saved_functions = json.load(f)
            return True
        except Exception as e:
            print(f"Erro ao carregar: {e}")
            return False
    
    def export_functions(self, filepath: str):
        """Exporta funções para JSON"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.saved_functions, f, indent=2)
            return True, f"Funções exportadas para {filepath}"
        except Exception as e:
            return False, f"Erro ao exportar: {str(e)}"
    
    def import_functions(self, filepath: str):
        """Importa funções de JSON"""
        try:
            with open(filepath, 'r') as f:
                self.saved_functions.update(json.load(f))
            self.save_to_disk()  # Auto-save após importar
            return True, f"Funções importadas de {filepath}"
        except Exception as e:
            return False, f"Erro ao importar: {str(e)}"


class CalculusModel(QObject):
    """Modelo para cálculo diferencial e integral"""
    
    def __init__(self):
        super().__init__()
        self.x, self.y, self.z, self.t = symbols('x y z t')
    
    def derivative(self, expr_str: str, var: str = 'x', order: int = 1):
        """Calcula derivada"""
        try:
            expr = sympify(expr_str)
            var_sym = getattr(self, var)
            result = diff(expr, var_sym, order)
            return True, result
        except Exception as e:
            return False, str(e)
    
    def integral(self, expr_str: str, var: str = 'x', limits=None):
        """Calcula integral"""
        try:
            expr = sympify(expr_str)
            var_sym = getattr(self, var)
            if limits:
                result = integrate(expr, (var_sym, limits[0], limits[1]))
            else:
                result = integrate(expr, var_sym)
            return True, result
        except Exception as e:
            return False, str(e)
    
    def solve_ode(self, ode_str: str, func_name: str = 'y'):
        """Resolve EDO"""
        try:
            y = Function(func_name)
            t = self.t
            # Substituir y' por Derivative(y(t), t)
            ode_str = ode_str.replace("y'", "Derivative(y(t), t)")
            ode_str = ode_str.replace("y''", "Derivative(y(t), t, 2)")
            ode_expr = sympify(ode_str, locals={'y': y, 't': t, 'Derivative': Derivative})
            
            if isinstance(ode_expr, bool):  # Se for equação como y' = x
                ode_expr = sympify(ode_str.replace('=', '-(') + ')', 
                                   locals={'y': y, 't': t, 'Derivative': Derivative})
            
            solution = dsolve(ode_expr, y(t))
            return True, solution
        except Exception as e:
            return False, f"Erro ao resolver EDO: {str(e)}"


class MatrixModel(QObject):
    """Modelo para operações matriciais"""
    
    def __init__(self):
        super().__init__()
        self.current_matrix = None
    
    def create_matrix(self, data: list):
        """Cria matriz a partir de lista"""
        try:
            self.current_matrix = Matrix(data)
            return True, self.current_matrix
        except Exception as e:
            return False, str(e)
    
    def determinant(self):
        """Calcula determinante"""
        if self.current_matrix is None:
            return False, "Nenhuma matriz definida"
        try:
            det = self.current_matrix.det()
            return True, det
        except Exception as e:
            return False, str(e)
    
    def inverse(self):
        """Calcula matriz inversa"""
        if self.current_matrix is None:
            return False, "Nenhuma matriz definida"
        try:
            inv = self.current_matrix.inv()
            return True, inv
        except Exception as e:
            return False, str(e)
    
    def eigenvalues(self):
        """Calcula autovalores"""
        if self.current_matrix is None:
            return False, "Nenhuma matriz definida"
        try:
            eigvals = self.current_matrix.eigenvals()
            return True, eigvals
        except Exception as e:
            return False, str(e)
    
    def transpose(self):
        """Calcula transposta"""
        if self.current_matrix is None:
            return False, "Nenhuma matriz definida"
        try:
            trans = self.current_matrix.T
            return True, trans
        except Exception as e:
            return False, str(e)


class JuliaExecutor(QObject):
    """Executor de scripts Julia com processo dedicado"""
    
    output_signal = Signal(str, str)
    
    def __init__(self):
        super().__init__()
        self.process = None
        self.julia_path = "julia"
    
    def execute(self, code: str):
        """Executa código Julia"""
        try:
            # Salva código em arquivo temporário
            temp_file = "/tmp/temp_julia_script.jl"
            with open(temp_file, 'w') as f:
                f.write(code)
            
            # Executa Julia
            result = subprocess.run(
                [self.julia_path, temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            self.output_signal.emit(result.stdout, result.stderr)
            os.remove(temp_file)
        except FileNotFoundError:
            self.output_signal.emit("", "Julia não encontrado. Instale Julia e adicione ao PATH.")
        except subprocess.TimeoutExpired:
            self.output_signal.emit("", "Timeout: Script Julia demorou muito.")
        except Exception as e:
            self.output_signal.emit("", str(e))
    
    def check_julia_available(self):
        """Verifica se Julia está disponível"""
        try:
            result = subprocess.run([self.julia_path, "--version"], 
                                    capture_output=True, text=True, timeout=5)
            return True, result.stdout.strip()
        except:
            return False, "Julia não encontrado"


class ScriptExecutor(QObject):
    """Executor de scripts Python"""
    
    output_signal = Signal(str, str)
    
    def execute_python(self, code: str):
        """Executa código Python"""
        output_buffer = StringIO()
        error_buffer = StringIO()
        
        try:
            with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
                exec(code, {
                    'np': np,
                    'sp': sp,
                    'symbols': symbols,
                    'sin': sin, 'cos': cos, 'tan': tan,
                    'exp': exp, 'log': log, 'sqrt': sqrt, 'pi': pi,
                    'diff': diff, 'integrate': integrate, 'Matrix': Matrix,
                    'solve': solve, 'dsolve': dsolve
                })
            self.output_signal.emit(output_buffer.getvalue(), "")
        except Exception as e:
            self.output_signal.emit("", str(e))


# ============================================================================
# VIEW - Interface Gráfica
# ============================================================================

class ConsoleWidget(QWidget):
    """Console CLI com Rich integrado"""
    
    command_signal = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.command_history = []
        self.history_index = -1
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Área de output
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Courier New", 10))
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3e3e3e;
            }
        """)
        
        # Input de comando
        input_layout = QHBoxLayout()
        self.prompt_label = QLabel(">>>")
        self.prompt_label.setStyleSheet("color: #4ec9b0; font-weight: bold;")
        self.command_input = QLineEdit()
        self.command_input.setFont(QFont("Courier New", 10))
        self.command_input.setStyleSheet("""
            QLineEdit {
                background-color: #252526;
                color: #d4d4d4;
                border: 1px solid #3e3e3e;
                padding: 5px;
            }
        """)
        self.command_input.returnPressed.connect(self.execute_command)
        
        input_layout.addWidget(self.prompt_label)
        input_layout.addWidget(self.command_input)
        
        layout.addWidget(self.output_text)
        layout.addLayout(input_layout)
        self.setLayout(layout)
        
        self.print_welcome()
    
    def print_welcome(self):
        """Imprime mensagem de boas-vindas"""
        welcome = """
╔════════════════════════════════════════════════════════════╗
║    Calculadora Científica Avançada v2.0 - Console CLI     ║
║    SymPy + Julia + PySide6 + Rich                         ║
╚════════════════════════════════════════════════════════════╝

Comandos disponíveis:
  help       - Mostra ajuda completa
  clear      - Limpa console
  vars       - Mostra variáveis disponíveis
  python ... - Executa código Python
  julia ...  - Executa código Julia
  save       - Salva função atual
  load       - Carrega função salva
  guide      - Mostra guia de uso
"""
        self.append_output(welcome, color="#4ec9b0")
    
    def execute_command(self):
        """Executa comando digitado"""
        command = self.command_input.text().strip()
        if not command:
            return
        
        self.command_history.append(command)
        self.history_index = len(self.command_history)
        
        self.append_output(f">>> {command}", color="#569cd6")
        self.command_signal.emit(command)
        self.command_input.clear()
    
    def append_output(self, text: str, color: str = "#d4d4d4"):
        """Adiciona texto ao output"""
        cursor = self.output_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        format = cursor.charFormat()
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        
        cursor.insertText(text + "\n")
        self.output_text.setTextCursor(cursor)
        self.output_text.ensureCursorVisible()
    
    def clear_console(self):
        """Limpa console"""
        self.output_text.clear()
        self.print_welcome()


class JuliaTerminalWidget(QWidget):
    """Terminal Julia interativo dedicado"""
    
    def __init__(self):
        super().__init__()
        self.julia_executor = JuliaExecutor()
        self.julia_executor.output_signal.connect(self.handle_output)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Info de status
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Status: Verificando Julia...")
        self.check_button = QPushButton("Verificar Julia")
        self.check_button.clicked.connect(self.check_julia)
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.check_button)
        status_layout.addStretch()
        
        # Área de script
        script_group = QGroupBox("Script Julia")
        script_layout = QVBoxLayout()
        
        self.script_text = QTextEdit()
        self.script_text.setFont(QFont("Courier New", 10))
        self.script_text.setPlaceholderText("""# Digite seu código Julia aqui
using SymPy

@vars x y z

expr = x^2 + y^2 + z^2
println("Expressão: ", expr)
println("Derivada em x: ", diff(expr, x))
""")
        
        buttons_layout = QHBoxLayout()
        self.run_button = QPushButton("▶ Executar Script")
        self.run_button.clicked.connect(self.run_script)
        self.clear_script_button = QPushButton("🗑 Limpar Script")
        self.clear_script_button.clicked.connect(lambda: self.script_text.clear())
        self.load_script_button = QPushButton("📁 Carregar .jl")
        self.load_script_button.clicked.connect(self.load_script)
        
        buttons_layout.addWidget(self.run_button)
        buttons_layout.addWidget(self.clear_script_button)
        buttons_layout.addWidget(self.load_script_button)
        buttons_layout.addStretch()
        
        script_layout.addWidget(self.script_text)
        script_layout.addLayout(buttons_layout)
        script_group.setLayout(script_layout)
        
        # Output
        output_group = QGroupBox("Saída Julia")
        output_layout = QVBoxLayout()
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Courier New", 9))
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
        """)
        
        clear_output_button = QPushButton("Limpar Saída")
        clear_output_button.clicked.connect(lambda: self.output_text.clear())
        
        output_layout.addWidget(self.output_text)
        output_layout.addWidget(clear_output_button)
        output_group.setLayout(output_layout)
        
        # Splitter para redimensionar
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(script_group)
        splitter.addWidget(output_group)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        layout.addLayout(status_layout)
        layout.addWidget(splitter)
        self.setLayout(layout)
        
        # Verifica Julia ao iniciar
        self.check_julia()
    
    def check_julia(self):
        """Verifica disponibilidade do Julia"""
        available, info = self.julia_executor.check_julia_available()
        if available:
            self.status_label.setText(f"✓ Julia disponível: {info}")
            self.status_label.setStyleSheet("color: #4ec9b0;")
        else:
            self.status_label.setText("✗ Julia não encontrado")
            self.status_label.setStyleSheet("color: #f48771;")
    
    def run_script(self):
        """Executa script Julia"""
        code = self.script_text.toPlainText()
        if code.strip():
            self.output_text.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            self.output_text.append(f"Executando em {datetime.now().strftime('%H:%M:%S')}...")
            self.julia_executor.execute(code)
    
    def handle_output(self, stdout: str, stderr: str):
        """Processa saída do Julia"""
        if stdout:
            self.output_text.append("Saída:")
            self.output_text.append(stdout)
        if stderr:
            self.output_text.setTextColor(QColor("#f48771"))
            self.output_text.append("Erro:")
            self.output_text.append(stderr)
            self.output_text.setTextColor(QColor("#d4d4d4"))
    
    def load_script(self):
        """Carrega script .jl de arquivo"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Carregar Script Julia", "", "Julia Files (*.jl);;All Files (*)"
        )
        if filepath:
            try:
                with open(filepath, 'r') as f:
                    self.script_text.setText(f.read())
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Erro ao carregar: {str(e)}")


class ScientificCalculatorWidget(QWidget):
    """Calculadora científica com display de expressões SymPy e botões numéricos"""
    
    def __init__(self, function_model: FunctionModel, calculus_model: CalculusModel):
        super().__init__()
        self.function_model = function_model
        self.calculus_model = calculus_model
        self.current_expression = ""
        init_printing(use_unicode=True)  # Habilita pretty printing
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Display de expressão com pretty printing
        display_group = QGroupBox("Expressão Matemática")
        display_layout = QVBoxLayout()
        
        # Display principal (pretty printing estilo Jupyter)
        self.pretty_display = QTextEdit()
        self.pretty_display.setReadOnly(True)
        self.pretty_display.setFont(QFont("Courier New", 12))
        self.pretty_display.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                color: #000000;
                border: 2px solid #4ec9b0;
                padding: 10px;
            }
        """)
        self.pretty_display.setMinimumHeight(120)
        self.pretty_display.setMaximumHeight(150)
        
        # Input de expressão (editable)
        self.expression_input = QLineEdit()
        self.expression_input.setFont(QFont("Courier New", 11))
        self.expression_input.setPlaceholderText("Digite ou use os botões abaixo...")
        self.expression_input.textChanged.connect(self.update_pretty_display)
        
        display_layout.addWidget(QLabel("📺 Display Pretty Printing:"))
        display_layout.addWidget(self.pretty_display)
        display_layout.addWidget(QLabel("✏️ Entrada:"))
        display_layout.addWidget(self.expression_input)
        
        # Botões de ação rápida
        quick_buttons_layout = QHBoxLayout()
        self.set_expr_button = QPushButton("✓ Definir")
        self.set_expr_button.clicked.connect(self.set_expression)
        self.simplify_button = QPushButton("⚡ Simplificar")
        self.simplify_button.clicked.connect(self.simplify_expr)
        self.expand_button = QPushButton("📏 Expandir")
        self.expand_button.clicked.connect(self.expand_expr)
        self.factor_button = QPushButton("🔢 Fatorar")
        self.factor_button.clicked.connect(self.factor_expr)
        self.clear_button = QPushButton("🗑 Limpar")
        self.clear_button.clicked.connect(self.clear_expression)
        
        quick_buttons_layout.addWidget(self.set_expr_button)
        quick_buttons_layout.addWidget(self.simplify_button)
        quick_buttons_layout.addWidget(self.expand_button)
        quick_buttons_layout.addWidget(self.factor_button)
        quick_buttons_layout.addWidget(self.clear_button)
        
        display_layout.addLayout(quick_buttons_layout)
        display_group.setLayout(display_layout)
        
        # ========== TECLADO NUMÉRICO E OPERAÇÕES ==========
        keyboard_group = QGroupBox("🔢 Teclado Científico")
        keyboard_layout = QGridLayout()
        
        # Botões numéricos e operações básicas
        buttons = [
            ('7', 0, 0), ('8', 0, 1), ('9', 0, 2), ('/', 0, 3), ('C', 0, 4),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2), ('*', 1, 3), ('(', 1, 4),
            ('1', 2, 0), ('2', 2, 1), ('3', 2, 2), ('-', 2, 3), (')', 2, 4),
            ('0', 3, 0), ('.', 3, 1), ('**', 3, 2), ('+', 3, 3), ('⌫', 3, 4),
        ]
        
        for text, row, col in buttons:
            btn = QPushButton(text)
            btn.setMinimumHeight(40)
            btn.setFont(QFont("Arial", 12, QFont.Bold))
            if text in ['C', '⌫']:
                btn.setStyleSheet("background-color: #d9534f; color: white;")
            elif text in ['+', '-', '*', '/', '**']:
                btn.setStyleSheet("background-color: #5bc0de; color: white;")
            elif text in ['(', ')']:
                btn.setStyleSheet("background-color: #f0ad4e; color: white;")
            else:
                btn.setStyleSheet("background-color: #5cb85c; color: white;")
            
            btn.clicked.connect(lambda checked, t=text: self.button_clicked(t))
            keyboard_layout.addWidget(btn, row, col)
        
        # Botões de funções matemáticas
        func_buttons = [
            ('x', 4, 0), ('y', 4, 1), ('z', 4, 2), ('t', 4, 3), ('π', 4, 4),
            ('sin(', 5, 0), ('cos(', 5, 1), ('tan(', 5, 2), ('exp(', 5, 3), ('log(', 5, 4),
            ('sqrt(', 6, 0), ('abs(', 6, 1), ('^2', 6, 2), ('^3', 6, 3), ('1/x', 6, 4),
        ]
        
        for text, row, col in func_buttons:
            btn = QPushButton(text)
            btn.setMinimumHeight(35)
            btn.setFont(QFont("Arial", 10))
            btn.setStyleSheet("background-color: #9b59b6; color: white;")
            btn.clicked.connect(lambda checked, t=text: self.function_clicked(t))
            keyboard_layout.addWidget(btn, row, col)
        
        keyboard_group.setLayout(keyboard_layout)
        
        # Operações de cálculo
        calc_group = QGroupBox("📐 Operações de Cálculo")
        calc_layout = QGridLayout()
        
        # Derivada
        calc_layout.addWidget(QLabel("Derivada:"), 0, 0)
        self.deriv_var = QComboBox()
        self.deriv_var.addItems(['x', 'y', 'z', 't'])
        calc_layout.addWidget(self.deriv_var, 0, 1)
        self.deriv_order = QSpinBox()
        self.deriv_order.setRange(1, 5)
        self.deriv_order.setValue(1)
        calc_layout.addWidget(QLabel("Ordem:"), 0, 2)
        calc_layout.addWidget(self.deriv_order, 0, 3)
        self.deriv_button = QPushButton("∂/∂x")
        self.deriv_button.clicked.connect(self.calculate_derivative)
        calc_layout.addWidget(self.deriv_button, 0, 4)
        
        # Integral
        calc_layout.addWidget(QLabel("Integral:"), 1, 0)
        self.integ_var = QComboBox()
        self.integ_var.addItems(['x', 'y', 'z', 't'])
        calc_layout.addWidget(self.integ_var, 1, 1)
        self.integ_button = QPushButton("∫ dx")
        self.integ_button.clicked.connect(self.calculate_integral)
        calc_layout.addWidget(self.integ_button, 1, 2, 1, 3)
        
        calc_group.setLayout(calc_layout)
        
        # Resultado
        result_group = QGroupBox("📊 Resultado")
        result_layout = QVBoxLayout()
        
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setFont(QFont("Courier New", 10))
        self.result_display.setMaximumHeight(150)
        self.result_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #4ec9b0;
            }
        """)
        
        result_layout.addWidget(self.result_display)
        result_group.setLayout(result_layout)
        
        layout.addWidget(display_group)
        layout.addWidget(keyboard_group)
        layout.addWidget(calc_group)
        layout.addWidget(result_group)
        
        self.setLayout(layout)
    
    def button_clicked(self, text):
        """Handler para botões numéricos e operações"""
        if text == 'C':
            self.expression_input.clear()
        elif text == '⌫':
            current = self.expression_input.text()
            self.expression_input.setText(current[:-1])
        else:
            current = self.expression_input.text()
            self.expression_input.setText(current + text)
    
    def function_clicked(self, text):
        """Handler para botões de funções matemáticas"""
        current = self.expression_input.text()
        
        if text == 'π':
            self.expression_input.setText(current + 'pi')
        elif text == '^2':
            self.expression_input.setText(current + '**2')
        elif text == '^3':
            self.expression_input.setText(current + '**3')
        elif text == '1/x':
            self.expression_input.setText(current + '1/')
        else:
            self.expression_input.setText(current + text)
    
    def update_pretty_display(self):
        """Atualiza display com pretty printing estilo Jupyter"""
        expr_str = self.expression_input.text()
        if not expr_str:
            self.pretty_display.clear()
            return
        
        try:
            expr = sympify(expr_str, locals={
                'x': self.function_model.x,
                'y': self.function_model.y,
                'z': self.function_model.z,
                't': self.function_model.t
            })
            
            # Usa pretty() do SymPy para formatação ASCII art
            pretty_str = pretty(expr, use_unicode=True)
            
            # Configura fonte monoespaçada para preservar alinhamento
            self.pretty_display.setPlainText(pretty_str)
            
        except Exception as e:
            self.pretty_display.setPlainText(f"Expressão inválida")
    
    def clear_expression(self):
        """Limpa expressão"""
        self.expression_input.clear()
        self.pretty_display.clear()
        self.current_expression = ""
    
    def set_expression(self):
        """Define expressão no display"""
        expr_str = self.expression_input.text()
        if expr_str:
            try:
                expr = sympify(expr_str)
                self.current_expression = expr
                self.result_display.append(f"✓ Expressão definida: {expr}\n")
                self.update_pretty_display()
            except Exception as e:
                self.result_display.append(f"✗ Erro: {str(e)}\n")
    
    def simplify_expr(self):
        """Simplifica expressão"""
        expr_str = self.expression_input.text()
        if expr_str:
            try:
                expr = sympify(expr_str)
                result = simplify(expr)
                self.expression_input.setText(str(result))
                self.result_display.append(f"Simplificado: {result}\n")
            except Exception as e:
                self.result_display.append(f"✗ Erro: {str(e)}\n")
    
    def expand_expr(self):
        """Expande expressão"""
        expr_str = self.expression_input.text()
        if expr_str:
            try:
                expr = sympify(expr_str)
                result = expand(expr)
                self.expression_input.setText(str(result))
                self.result_display.append(f"Expandido: {result}\n")
            except Exception as e:
                self.result_display.append(f"✗ Erro: {str(e)}\n")
    
    def factor_expr(self):
        """Fatorar expressão"""
        expr_str = self.expression_input.text()
        if expr_str:
            try:
                expr = sympify(expr_str)
                result = factor(expr)
                self.expression_input.setText(str(result))
                self.result_display.append(f"Fatorado: {result}\n")
            except Exception as e:
                self.result_display.append(f"Não foi possível fatorar\n")
    
    def calculate_derivative(self):
        """Calcula derivada"""
        expr_str = self.expression_input.text()
        if not expr_str:
            return
        
        var = self.deriv_var.currentText()
        order = self.deriv_order.value()
        
        success, result = self.calculus_model.derivative(expr_str, var, order)
        if success:
            self.result_display.append(f"d^{order}/d{var}^{order} = {result}\n")
            # Mostra pretty print do resultado
            pretty_result = pretty(result, use_unicode=True)
            self.result_display.append(f"\n{pretty_result}\n")
        else:
            self.result_display.append(f"✗ Erro: {result}\n")
    
    def calculate_integral(self):
        """Calcula integral"""
        expr_str = self.expression_input.text()
        if not expr_str:
            return
        
        var = self.integ_var.currentText()
        
        success, result = self.calculus_model.integral(expr_str, var)
        if success:
            self.result_display.append(f"∫ d{var} = {result} + C\n")
            # Mostra pretty print do resultado
            pretty_result = pretty(result, use_unicode=True)
            self.result_display.append(f"\n{pretty_result}\n")
        else:
            self.result_display.append(f"✗ Erro: {result}\n")


class ODESolverWidget(QWidget):
    """Widget para resolver EDOs"""
    
    def __init__(self, calculus_model: CalculusModel):
        super().__init__()
        self.calculus_model = calculus_model
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # EDO de 1ª ordem
        ode1_group = QGroupBox("EDO de 1ª Ordem: y' = f(t, y)")
        ode1_layout = QVBoxLayout()
        
        self.ode1_input = QLineEdit()
        self.ode1_input.setPlaceholderText("Ex: Derivative(y(t), t) - y(t)")
        
        ode1_examples = QComboBox()
        ode1_examples.addItems([
            "Selecione exemplo...",
            "y' = y  →  Derivative(y(t), t) - y(t)",
            "y' = 2*t  →  Derivative(y(t), t) - 2*t",
            "y' = -k*y  →  Derivative(y(t), t) + k*y(t)"
        ])
        ode1_examples.currentTextChanged.connect(
            lambda text: self.load_ode_example(text, self.ode1_input)
        )
        
        ode1_button = QPushButton("Resolver EDO 1ª Ordem")
        ode1_button.clicked.connect(lambda: self.solve_ode(self.ode1_input.text()))
        
        ode1_layout.addWidget(QLabel("Exemplos:"))
        ode1_layout.addWidget(ode1_examples)
        ode1_layout.addWidget(QLabel("Equação:"))
        ode1_layout.addWidget(self.ode1_input)
        ode1_layout.addWidget(ode1_button)
        ode1_group.setLayout(ode1_layout)
        
        # EDO de 2ª ordem
        ode2_group = QGroupBox("EDO de 2ª Ordem: y'' = f(t, y, y')")
        ode2_layout = QVBoxLayout()
        
        self.ode2_input = QLineEdit()
        self.ode2_input.setPlaceholderText("Ex: Derivative(y(t), t, 2) + y(t)")
        
        ode2_examples = QComboBox()
        ode2_examples.addItems([
            "Selecione exemplo...",
            "y'' + y = 0  →  Derivative(y(t), t, 2) + y(t)",
            "y'' - 4*y = 0  →  Derivative(y(t), t, 2) - 4*y(t)",
            "y'' + 2*y' + y = 0  →  Derivative(y(t), t, 2) + 2*Derivative(y(t), t) + y(t)"
        ])
        ode2_examples.currentTextChanged.connect(
            lambda text: self.load_ode_example(text, self.ode2_input)
        )
        
        ode2_button = QPushButton("Resolver EDO 2ª Ordem")
        ode2_button.clicked.connect(lambda: self.solve_ode(self.ode2_input.text()))
        
        ode2_layout.addWidget(QLabel("Exemplos:"))
        ode2_layout.addWidget(ode2_examples)
        ode2_layout.addWidget(QLabel("Equação:"))
        ode2_layout.addWidget(self.ode2_input)
        ode2_layout.addWidget(ode2_button)
        ode2_group.setLayout(ode2_layout)
        
        # Resultado
        result_group = QGroupBox("Solução")
        result_layout = QVBoxLayout()
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(QFont("Courier New", 10))
        self.result_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #4ec9b0;
            }
        """)
        
        result_layout.addWidget(self.result_text)
        result_group.setLayout(result_layout)
        
        layout.addWidget(ode1_group)
        layout.addWidget(ode2_group)
        layout.addWidget(result_group)
        
        self.setLayout(layout)
    
    def load_ode_example(self, text: str, input_widget: QLineEdit):
        """Carrega exemplo de EDO"""
        if "→" in text:
            ode = text.split("→")[1].strip()
            input_widget.setText(ode)
    
    def solve_ode(self, ode_str: str):
        """Resolve EDO"""
        if not ode_str:
            return
        
        success, result = self.calculus_model.solve_ode(ode_str)
        if success:
            self.result_text.append(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
            self.result_text.append(f"EDO: {ode_str}\n")
            self.result_text.append(f"Solução:\n{result}\n\n")
        else:
            self.result_text.append(f"✗ Erro: {result}\n")


class MatrixCalculatorWidget(QWidget):
    """Calculadora de matrizes"""
    
    def __init__(self, matrix_model: MatrixModel):
        super().__init__()
        self.matrix_model = matrix_model
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Configuração de matriz
        config_layout = QHBoxLayout()
        config_layout.addWidget(QLabel("Dimensão:"))
        self.rows_spin = QSpinBox()
        self.rows_spin.setRange(2, 5)
        self.rows_spin.setValue(3)
        self.rows_spin.valueChanged.connect(self.create_table)
        config_layout.addWidget(QLabel("Linhas:"))
        config_layout.addWidget(self.rows_spin)
        
        self.cols_spin = QSpinBox()
        self.cols_spin.setRange(2, 5)
        self.cols_spin.setValue(3)
        self.cols_spin.valueChanged.connect(self.create_table)
        config_layout.addWidget(QLabel("Colunas:"))
        config_layout.addWidget(self.cols_spin)
        config_layout.addStretch()
        
        # Tabela de matriz
        self.matrix_table = QTableWidget()
        self.create_table()
        
        # Botões de operações
        ops_layout = QGridLayout()
        
        self.det_button = QPushButton("Determinante")
        self.det_button.clicked.connect(self.calculate_determinant)
        ops_layout.addWidget(self.det_button, 0, 0)
        
        self.inv_button = QPushButton("Inversa")
        self.inv_button.clicked.connect(self.calculate_inverse)
        ops_layout.addWidget(self.inv_button, 0, 1)
        
        self.trans_button = QPushButton("Transposta")
        self.trans_button.clicked.connect(self.calculate_transpose)
        ops_layout.addWidget(self.trans_button, 0, 2)
        
        self.eigen_button = QPushButton("Autovalores")
        self.eigen_button.clicked.connect(self.calculate_eigenvalues)
        ops_layout.addWidget(self.eigen_button, 1, 0)
        
        self.clear_button = QPushButton("Limpar")
        self.clear_button.clicked.connect(self.clear_matrix)
        ops_layout.addWidget(self.clear_button, 1, 1)
        
        # Resultado
        result_group = QGroupBox("Resultado")
        result_layout = QVBoxLayout()
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(QFont("Courier New", 10))
        self.result_text.setMaximumHeight(200)
        self.result_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #4ec9b0;
            }
        """)
        
        result_layout.addWidget(self.result_text)
        result_group.setLayout(result_layout)
        
        layout.addLayout(config_layout)
        layout.addWidget(QLabel("Matriz:"))
        layout.addWidget(self.matrix_table)
        layout.addLayout(ops_layout)
        layout.addWidget(result_group)
        
        self.setLayout(layout)
    
    def create_table(self):
        """Cria/recria tabela de matriz"""
        rows = self.rows_spin.value()
        cols = self.cols_spin.value()
        
        self.matrix_table.setRowCount(rows)
        self.matrix_table.setColumnCount(cols)
        
        # Inicializa com zeros
        for i in range(rows):
            for j in range(cols):
                item = QTableWidgetItem("0")
                self.matrix_table.setItem(i, j, item)
        
        self.matrix_table.resizeColumnsToContents()
    
    def get_matrix_data(self):
        """Obtém dados da matriz"""
        rows = self.matrix_table.rowCount()
        cols = self.matrix_table.columnCount()
        
        data = []
        for i in range(rows):
            row = []
            for j in range(cols):
                try:
                    value = float(self.matrix_table.item(i, j).text())
                    row.append(value)
                except:
                    row.append(0)
            data.append(row)
        
        return data
    
    def calculate_determinant(self):
        """Calcula determinante"""
        data = self.get_matrix_data()
        success, result = self.matrix_model.create_matrix(data)
        
        if success:
            success, det = self.matrix_model.determinant()
            if success:
                self.result_text.append(f"Determinante = {det}\n")
    
    def calculate_inverse(self):
        """Calcula inversa"""
        data = self.get_matrix_data()
        success, result = self.matrix_model.create_matrix(data)
        
        if success:
            success, inv = self.matrix_model.inverse()
            if success:
                self.result_text.append(f"Matriz Inversa:\n{inv}\n")
            else:
                self.result_text.append(f"✗ Erro: {inv}\n")
    
    def calculate_transpose(self):
        """Calcula transposta"""
        data = self.get_matrix_data()
        success, result = self.matrix_model.create_matrix(data)
        
        if success:
            success, trans = self.matrix_model.transpose()
            if success:
                self.result_text.append(f"Transposta:\n{trans}\n")
    
    def calculate_eigenvalues(self):
        """Calcula autovalores"""
        data = self.get_matrix_data()
        success, result = self.matrix_model.create_matrix(data)
        
        if success:
            success, eigvals = self.matrix_model.eigenvalues()
            if success:
                self.result_text.append(f"Autovalores:\n{eigvals}\n")
    
    def clear_matrix(self):
        """Limpa matriz"""
        self.create_table()
        self.result_text.clear()


class PlotWidget(QWidget):
    """Widget para plotagem 2D e 3D"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Canvas matplotlib
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        
        # Controles
        controls_layout = QHBoxLayout()
        
        self.plot_type_combo = QComboBox()
        self.plot_type_combo.addItems(["3D - Superfície", "3D - Contorno", "3D - Wireframe", 
                                        "2D - Linha", "2D - Contorno"])
        
        self.plot_button = QPushButton("📊 Plotar Função")
        self.clear_button = QPushButton("🗑 Limpar")
        self.clear_button.clicked.connect(self.clear_plot)
        
        controls_layout.addWidget(QLabel("Tipo:"))
        controls_layout.addWidget(self.plot_type_combo)
        controls_layout.addWidget(self.plot_button)
        controls_layout.addWidget(self.clear_button)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
    
    def plot_function(self, func, x_range, y_range, resolution, plot_type):
        """Plota função 2D ou 3D"""
        self.figure.clear()
        
        x = np.linspace(x_range[0], x_range[1], resolution)
        
        try:
            if plot_type.startswith("3D"):
                y = np.linspace(y_range[0], y_range[1], resolution)
                X, Y = np.meshgrid(x, y)
                Z = func(X, Y, 0)
                
                ax = self.figure.add_subplot(111, projection='3d')
                
                if "Superfície" in plot_type:
                    surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
                    self.figure.colorbar(surf, ax=ax, shrink=0.5)
                elif "Contorno" in plot_type:
                    ax.contour3D(X, Y, Z, 50, cmap='viridis')
                else:  # Wireframe
                    ax.plot_wireframe(X, Y, Z, color='blue', alpha=0.6)
                
                ax.set_xlabel('X')
                ax.set_ylabel('Y')
                ax.set_zlabel('Z')
                ax.set_title('Gráfico 3D - f(x,y,z)')
                
            else:  # 2D
                y = func(x, 0, 0)
                ax = self.figure.add_subplot(111)
                
                if "Linha" in plot_type:
                    ax.plot(x, y, 'b-', linewidth=2)
                    ax.grid(True, alpha=0.3)
                else:  # Contorno 2D
                    y_range_2d = np.linspace(y_range[0], y_range[1], resolution)
                    X, Y = np.meshgrid(x, y_range_2d)
                    Z = func(X, Y, 0)
                    contour = ax.contour(X, Y, Z, 20, cmap='viridis')
                    self.figure.colorbar(contour, ax=ax)
                
                ax.set_xlabel('X')
                ax.set_ylabel('Y' if "Contorno" in plot_type else 'f(x)')
                ax.set_title('Gráfico 2D - f(x)')
            
            self.canvas.draw()
            return True
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao plotar: {str(e)}")
            return False
    
    def clear_plot(self):
        """Limpa o gráfico"""
        self.figure.clear()
        self.canvas.draw()


class FunctionConfigWidget(QWidget):
    """Widget para configuração de funções com salvamento"""
    
    function_defined = Signal(str)
    
    def __init__(self, function_model: FunctionModel):
        super().__init__()
        self.function_model = function_model
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Grupo de definição de função
        function_group = QGroupBox("Definição da Função f(x,y,z)")
        function_layout = QVBoxLayout()
        
        # Presets de funções
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Exemplos:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "Selecione...",
            "Esfera: sqrt(x**2 + y**2 + z**2)",
            "Parabolóide: x**2 + y**2 - z",
            "Senoidal: sin(x) * cos(y)",
            "Gaussiana: exp(-(x**2 + y**2 + z**2))",
            "Campo E: 1/(x**2 + y**2 + z**2)",
            "Potencial: 1/sqrt(x**2 + y**2 + z**2)"
        ])
        self.preset_combo.currentTextChanged.connect(self.load_preset)
        preset_layout.addWidget(self.preset_combo)
        preset_layout.addStretch()
        
        function_layout.addLayout(preset_layout)
        
        # Input de função
        self.function_input = QTextEdit()
        self.function_input.setMaximumHeight(80)
        self.function_input.setPlaceholderText("Digite a expressão matemática")
        function_layout.addWidget(QLabel("Expressão f(x,y,z):"))
        function_layout.addWidget(self.function_input)
        
        # Botões
        buttons_layout = QHBoxLayout()
        self.define_button = QPushButton("Definir Função")
        self.define_button.clicked.connect(self.define_function)
        self.save_button = QPushButton("💾 Salvar")
        self.save_button.clicked.connect(self.save_function)
        self.load_button = QPushButton("📁 Carregar")
        self.load_button.clicked.connect(self.load_function)
        
        buttons_layout.addWidget(self.define_button)
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.load_button)
        
        function_layout.addLayout(buttons_layout)
        
        # Display da função atual
        self.current_function_label = QLabel("Função atual: Nenhuma")
        self.current_function_label.setStyleSheet("color: #4ec9b0; font-weight: bold;")
        function_layout.addWidget(self.current_function_label)
        
        function_group.setLayout(function_layout)
        layout.addWidget(function_group)
        
        # Grupo de parâmetros de plotagem
        plot_group = QGroupBox("Parâmetros de Plotagem")
        plot_layout = QFormLayout()
        
        self.x_range_min = QDoubleSpinBox()
        self.x_range_min.setRange(-100, 100)
        self.x_range_min.setValue(-5)
        
        self.x_range_max = QDoubleSpinBox()
        self.x_range_max.setRange(-100, 100)
        self.x_range_max.setValue(5)
        
        self.y_range_min = QDoubleSpinBox()
        self.y_range_min.setRange(-100, 100)
        self.y_range_min.setValue(-5)
        
        self.y_range_max = QDoubleSpinBox()
        self.y_range_max.setRange(-100, 100)
        self.y_range_max.setValue(5)
        
        self.resolution = QSpinBox()
        self.resolution.setRange(10, 200)
        self.resolution.setValue(50)
        
        plot_layout.addRow("X mín:", self.x_range_min)
        plot_layout.addRow("X máx:", self.x_range_max)
        plot_layout.addRow("Y mín:", self.y_range_min)
        plot_layout.addRow("Y máx:", self.y_range_max)
        plot_layout.addRow("Resolução:", self.resolution)
        
        plot_group.setLayout(plot_layout)
        layout.addWidget(plot_group)
        
        # Funções salvas
        saved_group = QGroupBox("Funções Salvas")
        saved_layout = QVBoxLayout()
        
        self.saved_list = QComboBox()
        self.update_saved_list()
        
        export_import_layout = QHBoxLayout()
        self.export_button = QPushButton("Exportar Todas")
        self.export_button.clicked.connect(self.export_functions)
        self.import_button = QPushButton("Importar")
        self.import_button.clicked.connect(self.import_functions)
        
        export_import_layout.addWidget(self.export_button)
        export_import_layout.addWidget(self.import_button)
        
        saved_layout.addWidget(self.saved_list)
        saved_layout.addLayout(export_import_layout)
        saved_group.setLayout(saved_layout)
        layout.addWidget(saved_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def load_preset(self, text):
        """Carrega preset de função"""
        if ":" in text:
            expr = text.split(":")[1].strip()
            self.function_input.setText(expr)
    
    def define_function(self):
        """Define função"""
        expr = self.function_input.toPlainText().strip()
        if expr:
            self.function_defined.emit(expr)
    
    def save_function(self):
        """Salva função atual"""
        name, ok = QInputDialog.getText(self, "Salvar Função", "Nome da função:")
        if ok and name:
            success, msg = self.function_model.save_function(name)
            QMessageBox.information(self, "Salvar", msg)
            if success:
                self.update_saved_list()
    
    def load_function(self):
        """Carrega função salva"""
        name = self.saved_list.currentText()
        if name and name != "Nenhuma função salva":
            success, msg = self.function_model.load_function(name)
            if success:
                self.function_input.setText(self.function_model.function_str)
                QMessageBox.information(self, "Carregar", msg)
    
    def update_saved_list(self):
        """Atualiza lista de funções salvas"""
        self.saved_list.clear()
        if self.function_model.saved_functions:
            self.saved_list.addItems(self.function_model.saved_functions.keys())
        else:
            self.saved_list.addItem("Nenhuma função salva")
    
    def export_functions(self):
        """Exporta funções para JSON"""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Exportar Funções", "", "JSON Files (*.json)"
        )
        if filepath:
            success, msg = self.function_model.export_functions(filepath)
            QMessageBox.information(self, "Exportar", msg)
    
    def import_functions(self):
        """Importa funções de JSON"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Importar Funções", "", "JSON Files (*.json)"
        )
        if filepath:
            success, msg = self.function_model.import_functions(filepath)
            QMessageBox.information(self, "Importar", msg)
            if success:
                self.update_saved_list()
    
    def update_current_function(self, func_str):
        """Atualiza display da função atual"""
        self.current_function_label.setText(f"Função atual: {func_str}")


# ============================================================================
# CONTROLLER - Controlador MVC
# ============================================================================

class CalculatorController(QObject):
    """Controlador principal da aplicação"""
    
    def __init__(self, function_model: FunctionModel, calculus_model: CalculusModel):
        super().__init__()
        self.function_model = function_model
        self.calculus_model = calculus_model
        self.python_executor = ScriptExecutor()
        self.julia_executor = JuliaExecutor()
        
    def handle_console_command(self, command: str, console: ConsoleWidget):
        """Processa comandos do console"""
        cmd_lower = command.lower().strip()
        
        if cmd_lower == "help":
            self.show_help(console)
            
        elif cmd_lower == "clear":
            console.clear_console()
            
        elif cmd_lower == "vars":
            console.append_output("Variáveis: x, y, z, t", color="#4fc1ff")
            console.append_output("Funções: sin, cos, tan, exp, log, sqrt, pi", color="#4fc1ff")
            console.append_output("Cálculo: diff, integrate, Matrix, solve, dsolve", color="#4fc1ff")
            
        elif cmd_lower == "guide":
            self.show_usage_guide(console)
            
        elif cmd_lower.startswith("python "):
            code = command[7:]
            self.python_executor.execute_python(code)
            
        elif cmd_lower.startswith("julia "):
            code = command[6:]
            self.julia_executor.execute(code)
            
        elif cmd_lower == "save":
            console.append_output("Use a aba 'Configuração' para salvar funções", color="#ce9178")
            
        else:
            # Tenta executar como código Python
            try:
                self.python_executor.execute_python(command)
            except Exception as e:
                console.append_output(f"Erro: {str(e)}", color="#f48771")
    
    def show_help(self, console: ConsoleWidget):
        """Mostra ajuda completa"""
        help_text = """
╔════════════════════════════════════════════════════════════╗
║                    AJUDA COMPLETA                          ║
╚════════════════════════════════════════════════════════════╝

COMANDOS BÁSICOS:
  help       - Mostra esta ajuda
  clear      - Limpa o console
  vars       - Lista variáveis e funções disponíveis
  guide      - Mostra guia de uso completo
  save       - Informações sobre salvar funções
  
EXECUTAR CÓDIGO:
  python <código>    - Executa Python
  julia <código>     - Executa Julia
  
  Ou digite diretamente código Python!

EXEMPLOS RÁPIDOS:
  >>> x, y = sp.symbols('x y')
  >>> sp.diff(x**2 + y**2, x)
  >>> sp.integrate(sin(x), x)
  >>> Matrix([[1,2],[3,4]]).det()
"""
        console.append_output(help_text, color="#ce9178")
    
    def show_usage_guide(self, console: ConsoleWidget):
        """Mostra guia de uso completo"""
        guide = """
╔════════════════════════════════════════════════════════════╗
║              GUIA DE USO - SALVAR FUNÇÕES                  ║
╚════════════════════════════════════════════════════════════╝

1. SALVAR FUNÇÃO PYTHON/SYMPY:
   Aba "Configuração" → Digite expressão → "Salvar"
   Exemplo: x**2 + y**2 + z**2
   
2. SALVAR SCRIPT JULIA:
   Aba "Terminal Julia" → Digite script → "Carregar .jl"
   Salve como arquivo .jl no sistema
   
3. EXPORTAR/IMPORTAR:
   Aba "Configuração" → "Exportar Todas" (JSON)
   Importar: "Importar" → Selecionar .json
   
4. USAR FUNÇÕES SALVAS:
   Aba "Configuração" → Lista "Funções Salvas" → "Carregar"
   
FORMATO JSON (exemplo):
{
  "esfera": {
    "expression": "sqrt(x**2 + y**2 + z**2)",
    "timestamp": "2026-02-06T10:30:00"
  }
}

ABAS DISPONÍVEIS:
  ⚙️  Configuração   - Define e salva funções
  🧮 Calculadora     - Cálculo simbólico com display
  🔢 Matrizes        - Operações matriciais
  📐 EDOs            - Resolve equações diferenciais
  🖥️  Console        - Terminal Python integrado
  💻 Julia           - Terminal Julia dedicado
  📊 Gráfico         - Visualização 2D/3D
"""
        console.append_output(guide, color="#ce9178")


# ============================================================================
# MAIN WINDOW - Janela Principal
# ============================================================================

class CalculatorMainWindow(QMainWindow):
    """Janela principal da aplicação"""
    
    def __init__(self):
        super().__init__()
        
        # Inicializa Models
        self.function_model = FunctionModel()
        self.calculus_model = CalculusModel()
        self.matrix_model = MatrixModel()
        
        # Inicializa Controller
        self.controller = CalculatorController(self.function_model, self.calculus_model)
        
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        """Configura interface"""
        self.setWindowTitle("Calculadora Científica Avançada v2.0 - SymPy + Julia")
        self.setGeometry(100, 100, 1500, 950)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout()
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Tab 1: Configuração de Função
        self.config_widget = FunctionConfigWidget(self.function_model)
        self.tabs.addTab(self.config_widget, "⚙️ Configuração")
        
        # Tab 2: Calculadora Científica
        self.calc_widget = ScientificCalculatorWidget(
            self.function_model, self.calculus_model
        )
        self.tabs.addTab(self.calc_widget, "🧮 Calculadora")
        
        # Tab 3: Matrizes
        self.matrix_widget = MatrixCalculatorWidget(self.matrix_model)
        self.tabs.addTab(self.matrix_widget, "🔢 Matrizes")
        
        # Tab 4: EDOs
        self.ode_widget = ODESolverWidget(self.calculus_model)
        self.tabs.addTab(self.ode_widget, "📐 EDOs")
        
        # Tab 5: Console CLI Python
        self.console_widget = ConsoleWidget()
        self.tabs.addTab(self.console_widget, "🖥️ Console Python")
        
        # Tab 6: Terminal Julia
        self.julia_widget = JuliaTerminalWidget()
        self.tabs.addTab(self.julia_widget, "💻 Terminal Julia")
        
        # Tab 7: Gráfico
        self.plot_widget = PlotWidget()
        self.tabs.addTab(self.plot_widget, "📊 Gráfico 2D/3D")
        
        main_layout.addWidget(self.tabs)
        central_widget.setLayout(main_layout)
        
        # Estilo
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QTabWidget::pane {
                border: 1px solid #3e3e3e;
                background-color: #252526;
            }
            QTabBar::tab {
                background-color: #2d2d30;
                color: #cccccc;
                padding: 8px 16px;
                margin: 2px;
            }
            QTabBar::tab:selected {
                background-color: #094771;
                color: white;
            }
            QGroupBox {
                color: #cccccc;
                border: 1px solid #3e3e3e;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #4ec9b0;
            }
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QLabel {
                color: #cccccc;
            }
        """)
    
    def connect_signals(self):
        """Conecta sinais e slots"""
        # Configuração de função
        self.config_widget.function_defined.connect(self.define_function)
        self.function_model.function_updated.connect(
            self.config_widget.update_current_function
        )
        
        # Console
        self.console_widget.command_signal.connect(
            lambda cmd: self.controller.handle_console_command(cmd, self.console_widget)
        )
        
        # Executores de scripts
        self.controller.python_executor.output_signal.connect(self.handle_python_output)
        self.controller.julia_executor.output_signal.connect(self.handle_julia_output)
        
        # Plotagem
        self.plot_widget.plot_button.clicked.connect(self.plot_current_function)
    
    def define_function(self, expr: str):
        """Define função no modelo"""
        success, message = self.function_model.set_function(expr)
        
        if success:
            self.console_widget.append_output(message, color="#4ec9b0")
        else:
            self.console_widget.append_output(message, color="#f48771")
            QMessageBox.warning(self, "Erro", message)
    
    def plot_current_function(self):
        """Plota função atual"""
        func = self.function_model.get_numpy_function()
        
        if func is None:
            QMessageBox.warning(self, "Aviso", "Defina uma função primeiro!")
            return
        
        x_range = (self.config_widget.x_range_min.value(),
                   self.config_widget.x_range_max.value())
        y_range = (self.config_widget.y_range_min.value(),
                   self.config_widget.y_range_max.value())
        resolution = self.config_widget.resolution.value()
        plot_type = self.plot_widget.plot_type_combo.currentText()
        
        success = self.plot_widget.plot_function(func, x_range, y_range, resolution, plot_type)
        
        if success:
            self.console_widget.append_output("✓ Gráfico plotado!", color="#4ec9b0")
            self.tabs.setCurrentWidget(self.plot_widget)
    
    def handle_python_output(self, stdout: str, stderr: str):
        """Processa saída Python"""
        if stdout:
            self.console_widget.append_output(stdout, color="#4ec9b0")
        if stderr:
            self.console_widget.append_output(f"Erro: {stderr}", color="#f48771")
    
    def handle_julia_output(self, stdout: str, stderr: str):
        """Processa saída Julia"""
        if stdout:
            self.console_widget.append_output(f"[Julia] {stdout}", color="#4ec9b0")
        if stderr:
            self.console_widget.append_output(f"[Julia Erro] {stderr}", color="#f48771")


# ============================================================================
# MAIN - Ponto de Entrada
# ============================================================================

def main():
    """Função principal"""
    app = QApplication(sys.argv)
    
    # Define tema escuro
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    
    # Cria e mostra janela
    window = CalculatorMainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()