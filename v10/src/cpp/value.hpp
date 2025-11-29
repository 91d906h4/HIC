#pragma once

#include <memory>
#include <string>
#include <unordered_map>
#include <variant>
#include <vector>


namespace hic {

// Forward declarations
struct ArrayObject;
struct DictObject;

enum class ValueType {
  INT,
  FLOAT,
  STRING,
  BOOL,
  NONE,
  ARRAY_PTR,
  DICT_PTR,
  PYOBJECT_PTR
};

class Value {
public:
  ValueType type;

  // Union for primitive types
  union {
    int64_t int_val;
    double float_val;
    bool bool_val;
    int heap_ptr;
    void *py_object;
  };

  std::shared_ptr<std::string> str_val;

  // Constructors
  Value() : type(ValueType::NONE), int_val(0) {}
  Value(int64_t v) : type(ValueType::INT), int_val(v) {}
  Value(double v) : type(ValueType::FLOAT), float_val(v) {}
  Value(bool v) : type(ValueType::BOOL), bool_val(v) {}
  Value(const std::string &v)
      : type(ValueType::STRING), str_val(std::make_shared<std::string>(v)) {}
  Value(int ptr, ValueType t) : type(t), heap_ptr(ptr) {}

  // Static factory methods
  static Value None() { return Value(); }
  static Value Int(int64_t v) { return Value(v); }
  static Value Float(double v) { return Value(v); }
  static Value Bool(bool v) { return Value(v); }
  static Value String(const std::string &v) { return Value(v); }
  static Value ArrayPtr(int ptr) { return Value(ptr, ValueType::ARRAY_PTR); }
  static Value DictPtr(int ptr) { return Value(ptr, ValueType::DICT_PTR); }
  static Value PyObjectPtr(void *ptr) {
    Value v;
    v.type = ValueType::PYOBJECT_PTR;
    v.py_object = ptr;
    return v;
  }

  // Type checking
  bool isInt() const { return type == ValueType::INT; }
  bool isFloat() const { return type == ValueType::FLOAT; }
  bool isString() const { return type == ValueType::STRING; }
  bool isBool() const { return type == ValueType::BOOL; }
  bool isNone() const { return type == ValueType::NONE; }
  bool isArrayPtr() const { return type == ValueType::ARRAY_PTR; }
  bool isDictPtr() const { return type == ValueType::DICT_PTR; }
  bool isPyObject() const { return type == ValueType::PYOBJECT_PTR; }

  // Getters
  int64_t asInt() const { return int_val; }
  double asFloat() const {
    if (type == ValueType::INT)
      return static_cast<double>(int_val);
    return float_val;
  }
  bool asBool() const { return bool_val; }
  const std::string &asString() const { return *str_val; }
  int asHeapPtr() const { return heap_ptr; }
  void *asPyObject() const { return py_object; }

  // Conversion to string for printing
  std::string toString() const;

  // Type name
  std::string typeName() const;

  // Truthiness for conditionals
  bool isTruthy() const;
};

// Heap objects
struct HeapObject {
  virtual ~HeapObject() = default;
};

struct ArrayObject : HeapObject {
  std::vector<Value> elements;
};

struct DictObject : HeapObject {
  std::unordered_map<std::string, Value> pairs;
};

} // namespace hic
