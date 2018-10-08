"""
    This is a generic Parameter class, and a ChildParameter class.

    The Parameter class allows us to generate a parameter object,
    with a certain value and a name. The name space is incremental
    by defaul. Each Parameter object has a sympy symbol with its name.
    
    ChildParameter allows us to create dependent parameters, or complex
    expressions with their values related to the parent Parameters value. 
    This link is given by the initialization expression.


    TODO:
        1. Deal with displacement fields. 
            These are symbolic objects generated by Geometric Entities.
            If a displacement field is assosicated with a ChildParameter,
            the parent Parameter should take care of the dependent disp-
            lacement field(s).
        2. Parameter attribute is_variable
            I can see why we might need it, but perhaps the concept
            should be more clear.
"""

import sympy


class Parameter:
    _parameters_counter = 1

    def __init__(self, value, is_variable=True, name=None):
        self.value = value
        self.is_variable = is_variable
        if name is None:
            self.name = "p"
        else:
            self.name = name
        self.symbol = sympy.var(self.name + "_" + str(Parameter._parameters_counter))
        Parameter._parameters_counter += 1

        self.children = set()

    def __str__(self):
        _parameter_info = {
            "name": self.symbol,
            "value": self.value,
            "is_variable": self.is_variable,
        }
        return str(_parameter_info)

    def __repr__(self):
        return self.__str__()

    def _is_parameter_argument(self, arg):
        _is_parameter = isinstance(arg, Parameter) or isinstance(arg, ChildParameter)
        return _is_parameter

    def _is_numeric_argument(self, arg):
        _is_numeric = isinstance(arg, int) or isinstance(arg, float)
        return _is_numeric

    def __add__(self, other):
        """
        Arithmetic rule:
            - Parameter + int / float / Parameter -> ChildParameter
                Adding a number or a Parameter to another Parameter
                creates a connected (child) parameter. When the
                parents' values change, the child should also change.
        """
        if self._is_parameter_argument(other):
            return ChildParameter(self, other, expression=self.symbol + other.symbol)
        elif self._is_numeric_argument(other):
            return ChildParameter(self, expression=self.symbol + other)
        else:
            raise ValueError("int, float value or Parameter is required")

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return other + (-self)

    def __neg__(self):
        return ChildParameter(self, expression=-self.symbol)

    def __iadd__(self, other):
        if self.is_numeric_argument(other):
            self.value += other.value
            return self
        elif self._is_parameter_argument(other):
            _value_error_message = (
                "Cannot use Parameter.__iadd__ with another parameter."
                + " Use it with int / float."
            )
            ValueError(_value_error_message)
        else:
            raise ValueError("int or float value is required")

    def __mul__(self, other):
        if self._is_numeric_argument(other):
            return ChildParameter(self, expression=self.symbol * other)
        elif self._is_parameter_argument(other):
            return ChildParameter(self, other, expression=self.symbol * other.symbol)
        else:
            raise ValueError("int, float value or Parameter is required")

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if self._is_numeric_argument(other):
            return ChildParameter(self, expression=self.symbol / other)
        elif self._is_parameter_argument(other):
            return ChildParameter(self, other, expression=self.symbol / other.symbol)
        else:
            raise ValueError("int, float value or Parameter is required")

    def __rtruediv__(self, other):
        if self._is_numeric_argument(other):
            return ChildParameter(self, expression=other / self.symbol)
        elif self._is_parameter_argument(other):
            return ChildParameter(other, self, expression=other.symbol / self.symbol)
        else:
            raise ValueError("int, float value or Parameter is required")

    def add_child(self, child):
        self.children.add(child)


class ChildParameter(Parameter):
    """
        ChildParameter allows us to create dependent parameters.
        There is only one level of relationship, i.e. 
            child(child(parent)) == child(parent)
    """

    def __init__(self, *parents, expression=None):
        self.symbol = expression
        self.parents = parents

    def __str__(self):
        _child_parameter_info = {
            "value": self.value,
            "symbolic expression": self.symbol,
            "parent": self.parents,
        }
        return str(_child_parameter_info)

    @property
    def value(self):
        return self.symbol.subs(
            (parent.symbol, parent.value) for parent in self.parents
        )

    def set_parents(self, parents):
        self._parents = set()
        for parent in parents:
            if isinstance(parent, ChildParameter):
                self._parents.update(parent.parents)
            elif isinstance(parent, Parameter):
                self._parents.add(parent)
            else:
                raise ValueError(
                    "Cannot connect to non-Parameter object. Parameter of ChildParameter is required"
                )

        for parent in self._parents:
            parent.add_child(self)

    def get_parents(self):
        return self._parents

    parents = property(get_parents, set_parents)

    def add_child(self, child):
        self.parent.add_child(self)
