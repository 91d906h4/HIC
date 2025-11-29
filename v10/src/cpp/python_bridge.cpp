#include "vm.hpp"

#ifdef PYTHON_SUPPORT

namespace hic {

void VM::importPythonModule(const std::string &module_name) {
  PyObject *module = PyImport_ImportModule(module_name.c_str());
  if (!module) {
    PyErr_Print();
    error("Cannot import Python module: " + module_name);
  }
  python_modules[module_name] = module;
}

void VM::getPythonAttr(const std::string &attr_name) {
  Value obj = pop();

  PyObject *py_obj = nullptr;

  // Check if obj is a module name (string)
  if (obj.isString()) {
    std::string module_name = obj.asString();
    auto it = python_modules.find(module_name);
    if (it != python_modules.end()) {
      py_obj = it->second;
    } else {
      error("Module not found: " + module_name);
    }
  } else if (obj.isPyObject()) {
    py_obj = static_cast<PyObject *>(obj.asPyObject());
  } else {
    error("GET_ATTR requires module or Python object");
  }

  PyObject *attr = PyObject_GetAttrString(py_obj, attr_name.c_str());
  if (!attr) {
    PyErr_Print();
    error("Attribute not found: " + attr_name);
  }

  push(Value::PyObjectPtr(attr));
}

void VM::callPythonMethod(const std::string &method_info, int num_args) {
  // Pop arguments
  std::vector<Value> args;
  for (int i = 0; i < num_args; i++) {
    args.insert(args.begin(), pop());
  }

  // Pop object
  Value obj = pop();

  PyObject *py_obj = nullptr;

  // Check if obj is a module name or PyObject
  if (obj.isString()) {
    std::string module_name = obj.asString();
    auto it = python_modules.find(module_name);
    if (it != python_modules.end()) {
      py_obj = it->second;
    } else {
      error("Module not found: " + module_name);
    }
  } else if (obj.isPyObject()) {
    py_obj = static_cast<PyObject *>(obj.asPyObject());
  } else {
    error("CALL_METHOD requires module or Python object");
  }

  // Parse method_info to get method name
  size_t space_pos = method_info.find(' ');
  std::string method_name = method_info.substr(0, space_pos);

  // Get the method
  PyObject *method = PyObject_GetAttrString(py_obj, method_name.c_str());
  if (!method) {
    PyErr_Print();
    error("Method not found: " + method_name);
  }

  // Convert arguments to Python
  PyObject *py_args = PyTuple_New(num_args);
  for (int i = 0; i < num_args; i++) {
    PyObject *py_arg = valueToPython(args[i]);
    PyTuple_SetItem(py_args, i, py_arg);
  }

  // Call the method
  PyObject *result = PyObject_CallObject(method, py_args);
  Py_DECREF(py_args);
  Py_DECREF(method);

  if (!result) {
    PyErr_Print();
    error("Python method call failed: " + method_name);
  }

  // Convert result back to Value
  Value ret_val = pythonToValue(result);
  Py_DECREF(result);

  push(ret_val);
}

Value VM::pythonToValue(PyObject *obj) {
  if (obj == Py_None) {
    return Value::None();
  } else if (PyBool_Check(obj)) {
    return Value::Bool(obj == Py_True);
  } else if (PyLong_Check(obj)) {
    return Value::Int(PyLong_AsLongLong(obj));
  } else if (PyFloat_Check(obj)) {
    return Value::Float(PyFloat_AsDouble(obj));
  } else if (PyUnicode_Check(obj)) {
    const char *str = PyUnicode_AsUTF8(obj);
    return Value::String(str ? str : "");
  } else {
    // For other types, store as PyObject pointer
    Py_INCREF(obj);
    return Value::PyObjectPtr(obj);
  }
}

PyObject *VM::valueToPython(const Value &val) {
  switch (val.type) {
  case ValueType::NONE:
    Py_RETURN_NONE;
  case ValueType::BOOL:
    return PyBool_FromLong(val.asBool() ? 1 : 0);
  case ValueType::INT:
    return PyLong_FromLongLong(val.asInt());
  case ValueType::FLOAT:
    return PyFloat_FromDouble(val.asFloat());
  case ValueType::STRING:
    return PyUnicode_FromString(val.asString().c_str());
  case ValueType::PYOBJECT_PTR: {
    PyObject *obj = static_cast<PyObject *>(val.asPyObject());
    Py_INCREF(obj);
    return obj;
  }
  default:
    // For arrays/dicts, could convert to Python list/dict
    // For now, return None
    Py_RETURN_NONE;
  }
}

} // namespace hic

#endif // PYTHON_SUPPORT
