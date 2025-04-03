import math
from pygeofilter.backends.native.evaluate import NativeEvaluator

def filter_opportunity(ast, data):
    attr_map = {"*":"properties.*"}
    filter_expr = NativeEvaluator(math.__dict__, attr_map, use_getattr=True).evaluate(
        ast
    )
    return [opp for opp in data if filter_expr(opp)]