from calculator.calc import Calculator
from calculator.calc import CalculatorSource

if __name__ == "__main__":
    calculator = Calculator(grpc_host="calculator-dev.toggle:8080", calculator_source=CalculatorSource.grpc)
    data = calculator.calculate(snake="spx.price")
    print(data)
