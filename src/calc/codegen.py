from collections.abc import Iterable

import llvmlite.ir as ir
from lark import Transformer

from .parse import parser


class LLVMTransformer(Transformer):
    def __init__(self, builder: ir.IRBuilder, vars: dict[str, ir.AllocaInstr], input_fn: ir.Function):
        super().__init__()
        self._builder = builder
        self._vars = vars
        self._input_fn = input_fn
        self._double = ir.DoubleType()

    def number(self, items):
        return ir.Constant(self._double, float(str(items[0])))

    def neg(self, items):
        return self._builder.fsub(ir.Constant(self._double, 0.0), items[0])

    def add(self, items):
        return self._builder.fadd(items[0], items[1])

    def sub(self, items):
        return self._builder.fsub(items[0], items[1])

    def mul(self, items):
        return self._builder.fmul(items[0], items[1])

    def div(self, items):
        return self._builder.fdiv(items[0], items[1])

    def var(self, items):
        name = str(items[0])
        return self._builder.load(self._vars[name], name=name)

    def assign_var(self, items):
        name, value = str(items[0]), items[1]
        if name not in self._vars:
            self._vars[name] = self._builder.alloca(self._double, name=name)
        self._builder.store(value, self._vars[name])
        return value

    def define_var(self, items):
        name = str(items[0])
        name_const = ir.Constant(
            ir.ArrayType(ir.IntType(8), len(name) + 1),
            bytearray(name.encode() + b"\x00"),
        )
        name_global = ir.GlobalVariable(self._builder.module, name_const.type, name=f".str.{name}")
        name_global.global_constant = True
        name_global.initializer = name_const
        name_ptr = self._builder.bitcast(name_global, ir.IntType(8).as_pointer())
        value = self._builder.call(self._input_fn, [name_ptr])
        ptr = self._builder.alloca(self._double, name=name)
        self._vars[name] = ptr
        self._builder.store(value, ptr)


def compile_to_ir(expressions: Iterable[str]) -> str:
    module = ir.Module(name="calc")
    module.triple = "x86_64-pc-linux-gnu"

    double = ir.DoubleType()
    i8_ptr = ir.IntType(8).as_pointer()
    i32 = ir.IntType(32)

    # declare external: double input_var(i8* name)
    input_fn = ir.Function(module, ir.FunctionType(double, [i8_ptr]), name="input_var")

    # declare external: int printf(i8*, ...)
    printf_fn = ir.Function(module, ir.FunctionType(i32, [i8_ptr], var_arg=True), name="printf")

    # fmt string: "Result: %f\n"
    fmt_str = b"Result: %f\n\00"
    fmt_const = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt_str)), bytearray(fmt_str))
    fmt_global = ir.GlobalVariable(module, fmt_const.type, name=".fmt")
    fmt_global.global_constant = True
    fmt_global.initializer = fmt_const

    # define int @main()
    main_fn = ir.Function(module, ir.FunctionType(i32, []), name="main")
    block = main_fn.append_basic_block("entry")
    builder = ir.IRBuilder(block)

    vars: dict[str, ir.AllocaInstr] = {}
    transformer = LLVMTransformer(builder, vars, input_fn)

    result = None
    for expr in expressions:
        result = transformer.transform(parser.parse(expr))

    if result is None:
        raise ValueError("expressions produced no result")

    fmt_ptr = builder.bitcast(fmt_global, i8_ptr)
    builder.call(printf_fn, [fmt_ptr, result])
    builder.ret(ir.Constant(i32, 0))

    return str(module)
