#pragma once

#include "value.hpp"
#include <memory>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>


#ifdef PYTHON_SUPPORT
#include <Python.h>
#endif

namespace hic {

struct Instruction {
  std::string opcode;
  std::string arg;
};

class VM {
private:
  std::vector<Value> stack;
  std::vector<Instruction> code;
  std::unordered_map<std::string, int> labels;
  std::unordered_map<int, std::unique_ptr<HeapObject>> heap;

  int ip;       // Instruction pointer
  int fp;       // Frame pointer
  int heap_ptr; // Next heap pointer

  // Exception handling
  struct ExceptionHandler {
    std::string catch_label;
    size_t stack_size;
  };
  std::vector<ExceptionHandler> exception_handlers;
  std::string current_exception;

#ifdef PYTHON_SUPPORT
  // Python module registry
  std::unordered_map<std::string, PyObject *> python_modules;
#endif

public:
  VM();
  ~VM();

  // Load program from assembly file
  void loadProgram(const std::string &filename);

  // Execute the program
  void run();

private:
  // Stack operations
  void push(const Value &val);
  Value pop();
  Value &peek();

  // Heap operations
  int allocateArray();
  int allocateDict();
  ArrayObject *getArray(int ptr);
  DictObject *getDict(int ptr);

  // Instruction handlers
  void execute(const Instruction &instr);

  // Arithmetic operations
  Value add(const Value &a, const Value &b);
  Value sub(const Value &a, const Value &b);
  Value mul(const Value &a, const Value &b);
  Value div(const Value &a, const Value &b);

  // Comparison operations
  Value eq(const Value &a, const Value &b);
  Value neq(const Value &a, const Value &b);
  Value lt(const Value &a, const Value &b);
  Value gt(const Value &a, const Value &b);
  Value le(const Value &a, const Value &b);
  Value ge(const Value &a, const Value &b);

  // Built-in functions
  void builtinPrint();
  void builtinLen();
  void builtinStr();
  void builtinInt();
  void builtinTypeof();
  void builtinAbs();

#ifdef PYTHON_SUPPORT
  // Python integration
  void importPythonModule(const std::string &module_name);
  void getPythonAttr(const std::string &attr_name);
  void callPythonMethod(const std::string &method_name, int num_args);
  Value pythonToValue(PyObject *obj);
  PyObject *valueToPython(const Value &val);
#endif

  // Utility
  void error(const std::string &msg);
  int parseIntArg(const std::string &arg);
  double parseFloatArg(const std::string &arg);
};

} // namespace hic
