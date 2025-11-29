#include "vm.hpp"
#include <cmath>
#include <iostream>


namespace hic {

// Arithmetic operations
Value VM::add(const Value &a, const Value &b) {
  // String concatenation
  if (a.isString() || b.isString()) {
    return Value::String(a.toString() + b.toString());
  }
  // Float arithmetic
  if (a.isFloat() || b.isFloat()) {
    double av = a.isFloat() ? a.asFloat() : a.asInt();
    double bv = b.isFloat() ? b.asFloat() : b.asInt();
    return Value::Float(av + bv);
  }
  // Integer arithmetic
  return Value::Int(a.asInt() + b.asInt());
}

Value VM::sub(const Value &a, const Value &b) {
  if (a.isFloat() || b.isFloat()) {
    double av = a.isFloat() ? a.asFloat() : a.asInt();
    double bv = b.isFloat() ? b.asFloat() : b.asInt();
    return Value::Float(av - bv);
  }
  return Value::Int(a.asInt() - b.asInt());
}

Value VM::mul(const Value &a, const Value &b) {
  if (a.isFloat() || b.isFloat()) {
    double av = a.isFloat() ? a.asFloat() : a.asInt();
    double bv = b.isFloat() ? b.asFloat() : b.asInt();
    return Value::Float(av * bv);
  }
  return Value::Int(a.asInt() * b.asInt());
}

Value VM::div(const Value &a, const Value &b) {
  if (a.isFloat() || b.isFloat()) {
    double av = a.isFloat() ? a.asFloat() : a.asInt();
    double bv = b.isFloat() ? b.asFloat() : b.asInt();
    if (bv == 0.0)
      error("Division by zero");
    return Value::Float(av / bv);
  }
  int64_t bv = b.asInt();
  if (bv == 0)
    error("Division by zero");
  return Value::Int(a.asInt() / bv);
}

// Comparison operations
Value VM::eq(const Value &a, const Value &b) {
  if (a.type != b.type)
    return Value::Int(0);

  switch (a.type) {
  case ValueType::INT:
    return Value::Int(a.asInt() == b.asInt() ? 1 : 0);
  case ValueType::FLOAT:
    return Value::Int(a.asFloat() == b.asFloat() ? 1 : 0);
  case ValueType::STRING:
    return Value::Int(a.asString() == b.asString() ? 1 : 0);
  case ValueType::BOOL:
    return Value::Int(a.asBool() == b.asBool() ? 1 : 0);
  case ValueType::NONE:
    return Value::Int(1);
  default:
    return Value::Int(a.asHeapPtr() == b.asHeapPtr() ? 1 : 0);
  }
}

Value VM::neq(const Value &a, const Value &b) {
  return Value::Int(eq(a, b).asInt() == 0 ? 1 : 0);
}

Value VM::lt(const Value &a, const Value &b) {
  if (a.isFloat() || b.isFloat()) {
    double av = a.isFloat() ? a.asFloat() : a.asInt();
    double bv = b.isFloat() ? b.asFloat() : b.asInt();
    return Value::Int(av < bv ? 1 : 0);
  }
  return Value::Int(a.asInt() < b.asInt() ? 1 : 0);
}

Value VM::gt(const Value &a, const Value &b) {
  if (a.isFloat() || b.isFloat()) {
    double av = a.isFloat() ? a.asFloat() : a.asInt();
    double bv = b.isFloat() ? b.asFloat() : b.asInt();
    return Value::Int(av > bv ? 1 : 0);
  }
  return Value::Int(a.asInt() > b.asInt() ? 1 : 0);
}

Value VM::le(const Value &a, const Value &b) {
  if (a.isFloat() || b.isFloat()) {
    double av = a.isFloat() ? a.asFloat() : a.asInt();
    double bv = b.isFloat() ? b.asFloat() : b.asInt();
    return Value::Int(av <= bv ? 1 : 0);
  }
  return Value::Int(a.asInt() <= b.asInt() ? 1 : 0);
}

Value VM::ge(const Value &a, const Value &b) {
  if (a.isFloat() || b.isFloat()) {
    double av = a.isFloat() ? a.asFloat() : a.asInt();
    double bv = b.isFloat() ? b.asFloat() : b.asInt();
    return Value::Int(av >= bv ? 1 : 0);
  }
  return Value::Int(a.asInt() >= b.asInt() ? 1 : 0);
}

// Built-in functions
void VM::builtinPrint() {
  Value val = pop();
  std::cout << val.toString() << std::endl;
}

void VM::builtinLen() {
  Value obj = pop();
  if (obj.isString()) {
    push(Value::Int(obj.asString().length()));
  } else if (obj.isArrayPtr()) {
    ArrayObject *arr = getArray(obj.asHeapPtr());
    push(Value::Int(arr->elements.size()));
  } else if (obj.isDictPtr()) {
    DictObject *dict = getDict(obj.asHeapPtr());
    push(Value::Int(dict->pairs.size()));
  } else {
    error("len() requires string, array, or dict");
  }
}

void VM::builtinStr() {
  Value val = pop();
  push(Value::String(val.toString()));
}

void VM::builtinInt() {
  Value val = pop();
  if (val.isInt()) {
    push(val);
  } else if (val.isFloat()) {
    push(Value::Int(static_cast<int64_t>(val.asFloat())));
  } else if (val.isString()) {
    try {
      push(Value::Int(std::stoll(val.asString())));
    } catch (...) {
      push(Value::Int(0));
    }
  } else {
    push(Value::Int(0));
  }
}

void VM::builtinTypeof() {
  Value val = pop();
  push(Value::String(val.typeName()));
}

void VM::builtinAbs() {
  Value val = pop();
  if (val.isInt()) {
    push(Value::Int(std::abs(val.asInt())));
  } else if (val.isFloat()) {
    push(Value::Float(std::abs(val.asFloat())));
  } else {
    error("abs() requires numeric value");
  }
}

// Utility functions
void VM::error(const std::string &msg) { throw std::runtime_error(msg); }

int VM::parseIntArg(const std::string &arg) {
  try {
    return std::stoi(arg);
  } catch (...) {
    error("Invalid integer argument: " + arg);
    return 0;
  }
}

double VM::parseFloatArg(const std::string &arg) {
  try {
    return std::stod(arg);
  } catch (...) {
    error("Invalid float argument: " + arg);
    return 0.0;
  }
}

} // namespace hic
