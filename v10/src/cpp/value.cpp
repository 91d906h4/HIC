#include "value.hpp"
#include <iomanip>
#include <sstream>


namespace hic {

std::string Value::toString() const {
  switch (type) {
  case ValueType::INT:
    return std::to_string(int_val);
  case ValueType::FLOAT: {
    std::ostringstream oss;
    oss << float_val;
    return oss.str();
  }
  case ValueType::STRING:
    return *str_val;
  case ValueType::BOOL:
    return bool_val ? "True" : "False";
  case ValueType::NONE:
    return "None";
  case ValueType::ARRAY_PTR:
    return "[Array@" + std::to_string(heap_ptr) + "]";
  case ValueType::DICT_PTR:
    return "[Dict@" + std::to_string(heap_ptr) + "]";
  case ValueType::PYOBJECT_PTR:
    return "[PyObject@" +
           std::to_string(reinterpret_cast<intptr_t>(py_object)) + "]";
  default:
    return "[Unknown]";
  }
}

std::string Value::typeName() const {
  switch (type) {
  case ValueType::INT:
    return "int";
  case ValueType::FLOAT:
    return "float";
  case ValueType::STRING:
    return "string";
  case ValueType::BOOL:
    return "bool";
  case ValueType::NONE:
    return "none";
  case ValueType::ARRAY_PTR:
    return "array";
  case ValueType::DICT_PTR:
    return "dict";
  case ValueType::PYOBJECT_PTR:
    return "pyobject";
  default:
    return "unknown";
  }
}

bool Value::isTruthy() const {
  switch (type) {
  case ValueType::INT:
    return int_val != 0;
  case ValueType::FLOAT:
    return float_val != 0.0;
  case ValueType::STRING:
    return !str_val->empty();
  case ValueType::BOOL:
    return bool_val;
  case ValueType::NONE:
    return false;
  default:
    return true; // Arrays, dicts, objects are truthy
  }
}

} // namespace hic
