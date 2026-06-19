"""End-to-end semantics, including the quirk fixes and small additions."""

import pytest

from .conftest import run


def test_bit_shift_fixed():
    # The original VM had BSL/BSR swapped; these must now mean << and >>.
    assert run("print(1 << 5);") == ["32"]
    assert run("print(256 >> 2);") == ["64"]


def test_compound_assignment():
    src = """
    int a = 10;
    a += 5; print(a);
    a -= 3; print(a);
    a *= 2; print(a);
    """
    assert run(src) == ["15", "12", "24"]


def test_comparisons_yield_real_booleans():
    assert run("bool c = 3 > 2; print(c);") == ["true"]
    assert run("print(1 == 2);") == ["false"]
    assert run("print(not false or false);") == ["true"]


def test_arithmetic_precedence_and_pow():
    assert run("print(8 + 5 * 2);") == ["18"]
    assert run("print(2 ** 3 ** 2);") == ["512"]  # right associative


def test_string_concatenation():
    assert run('string s = "Hello" + ", " + "world"; print(s);') == ["Hello, world"]


def test_arrays_and_negative_index():
    src = """
    int x[3] = [10, 20, 30];
    print(x[0]);
    print(x[-1]);
    x[1] = 99;
    print(x[1]);
    """
    assert run(src) == ["10", "30", "99"]


def test_array_size_from_variable():
    src = """
    int n = 4;
    int a[n];
    for(int i = 0; i < n; i = i + 1){ a[i] = i * i; }
    print(a[3]);
    """
    assert run(src) == ["9"]


def test_postfix_and_prefix_increment():
    assert run("int i = 5; int j = i++; print(j); print(i);") == ["5", "6"]
    assert run("int i = 5; int j = ++i; print(j); print(i);") == ["6", "6"]


def test_while_loop():
    src = """
    int n = 0;
    int total = 0;
    while(n < 5){ total = total + n; n = n + 1; }
    print(total);
    """
    assert run(src) == ["10"]


def test_arguments_bind_left_to_right():
    # First parameter receives the first argument.
    src = """
    function sub(int a, int b){ return a - b; }
    print(sub(10, 3));
    """
    assert run(src) == ["7"]


def test_function_recursion():
    src = """
    function fib(int n){
        if(n <= 1){ return n; }
        return fib(n - 1) + fib(n - 2);
    }
    print(fib(10));
    """
    assert run(src) == ["55"]


def test_print_multiple_args_in_order():
    assert run("print(1, 2, 3);") == ["1", "2", "3"]


def test_roundtrip_matches_direct():
    src = "int a = 3 + 4 * 2; print(a);"
    assert run(src) == run(src, roundtrip=True)


def test_undefined_variable_raises():
    from hylang.errors import HyRuntimeError
    with pytest.raises(HyRuntimeError):
        run("print(nope);")
