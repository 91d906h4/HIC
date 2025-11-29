#include "vm.hpp"
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iostream>
#include <random>
#include <sstream>

namespace hic {

VM::VM() : ip(0), fp(0), heap_ptr(0) {
#ifdef PYTHON_SUPPORT
  Py_Initialize();
#endif
}

VM::~VM() {
#ifdef PYTHON_SUPPORT
  // Clean up Python modules
  for (auto &pair : python_modules) {
    Py_XDECREF(pair.second);
  }
  Py_Finalize();
#endif
}

void VM::loadProgram(const std::string &filename) {
  std::ifstream file(filename);
  if (!file.is_open()) {
    error("Cannot open file: " + filename);
  }

  std::string line;
  int addr = 0;
  std::vector<std::string> cleaned_lines;

  // First pass: collect labels
  while (std::getline(file, line)) {
    // Trim whitespace
    line.erase(0, line.find_first_not_of(" \t\r\n"));
    line.erase(line.find_last_not_of(" \t\r\n") + 1);

    if (line.empty())
      continue;

    if (line.back() == ':') {
      // Label
      std::string label = line.substr(0, line.length() - 1);
      labels[label] = addr;
    } else {
      cleaned_lines.push_back(line);
      addr++;
    }
  }

  // Second pass: parse instructions
  for (const auto &line : cleaned_lines) {
    size_t space_pos = line.find(' ');
    std::string opcode, arg;

    if (space_pos != std::string::npos) {
      opcode = line.substr(0, space_pos);
      arg = line.substr(space_pos + 1);

      // Handle STRING_NEW specially - preserve quoted strings
      if (opcode == "STRING_NEW" && arg.front() == '"' && arg.back() == '"') {
        arg = arg.substr(1, arg.length() - 2);
        // Unescape
        size_t pos = 0;
        while ((pos = arg.find("\\n", pos)) != std::string::npos) {
          arg.replace(pos, 2, "\n");
          pos++;
        }
        pos = 0;
        while ((pos = arg.find("\\t", pos)) != std::string::npos) {
          arg.replace(pos, 2, "\t");
          pos++;
        }
        pos = 0;
        while ((pos = arg.find("\\\\", pos)) != std::string::npos) {
          arg.replace(pos, 2, "\\");
          pos++;
        }
      }
    } else {
      opcode = line;
    }

    code.push_back({opcode, arg});
  }
}

void VM::run() {
  try {
    while (ip < static_cast<int>(code.size())) {
      execute(code[ip]);
      ip++;
    }
  } catch (const std::exception &e) {
    std::cerr << "Runtime Error: " << e.what() << std::endl;
    throw;
  }
}

void VM::push(const Value &val) { stack.push_back(val); }

Value VM::pop() {
  if (stack.empty()) {
    error("Stack underflow");
  }
  Value val = stack.back();
  stack.pop_back();
  return val;
}

Value &VM::peek() {
  if (stack.empty()) {
    error("Stack underflow");
  }
  return stack.back();
}

int VM::allocateArray() {
  int ptr = heap_ptr++;
  heap[ptr] = std::make_unique<ArrayObject>();
  return ptr;
}

int VM::allocateDict() {
  int ptr = heap_ptr++;
  heap[ptr] = std::make_unique<DictObject>();
  return ptr;
}

ArrayObject *VM::getArray(int ptr) {
  auto it = heap.find(ptr);
  if (it == heap.end()) {
    error("Invalid array pointer: " + std::to_string(ptr));
  }
  return dynamic_cast<ArrayObject *>(it->second.get());
}

DictObject *VM::getDict(int ptr) {
  auto it = heap.find(ptr);
  if (it == heap.end()) {
    error("Invalid dict pointer: " + std::to_string(ptr));
  }
  return dynamic_cast<DictObject *>(it->second.get());
}

// Helper for Mock Python Support
Value mockPythonCall(const std::string &module, const std::string &method,
                     const std::vector<Value> &args) {
  if (module == "math") {
    if (method == "sqrt" && args.size() == 1)
      return Value::Float(std::sqrt(args[0].asFloat()));
    if (method == "pow" && args.size() == 2)
      return Value::Float(std::pow(args[0].asFloat(), args[1].asFloat()));
    if (method == "sin" && args.size() == 1)
      return Value::Float(std::sin(args[0].asFloat()));
    if (method == "ceil" && args.size() == 1)
      return Value::Float(std::ceil(args[0].asFloat()));
    if (method == "floor" && args.size() == 1)
      return Value::Float(std::floor(args[0].asFloat()));
  } else if (module == "random") {
    if (method == "randint" && args.size() == 2) {
      return Value::Int(
          args[0].asInt() +
          (std::rand() % (args[1].asInt() - args[0].asInt() + 1)));
    }
    if (method == "random")
      return Value::Float((double)std::rand() / RAND_MAX);
  }
  return Value::None();
}

void VM::execute(const Instruction &instr) {
  const std::string &op = instr.opcode;
  const std::string &arg = instr.arg;

  // Stack operations
  if (op == "PUSH") {
    if (arg.find('.') != std::string::npos) {
      push(Value::Float(std::stod(arg)));
    } else {
      push(Value::Int(std::stoll(arg)));
    }
  } else if (op == "PUSH_TRUE") {
    push(Value::Bool(true));
  } else if (op == "PUSH_FALSE") {
    push(Value::Bool(false));
  } else if (op == "PUSH_NONE") {
    push(Value::None());
  } else if (op == "POP") {
    pop();
  } else if (op == "DUP") {
    push(peek());
  } else if (op == "LOAD") {
    int offset = parseIntArg(arg);
    if (fp + offset >= static_cast<int>(stack.size())) {
      error("Invalid LOAD offset: " + std::to_string(offset));
    }
    push(stack[fp + offset]);
  } else if (op == "STORE") {
    int offset = parseIntArg(arg);
    Value val = pop();
    int idx = fp + offset;
    // Extend stack if necessary
    while (static_cast<int>(stack.size()) <= idx) {
      stack.push_back(Value::Int(0));
    }
    stack[idx] = val;
  }

  // Arithmetic operations
  else if (op == "ADD") {
    Value b = pop();
    Value a = pop();
    push(add(a, b));
  } else if (op == "SUB") {
    Value b = pop();
    Value a = pop();
    push(sub(a, b));
  } else if (op == "MUL") {
    Value b = pop();
    Value a = pop();
    push(mul(a, b));
  } else if (op == "DIV") {
    Value b = pop();
    Value a = pop();
    push(div(a, b));
  }

  // Comparison operations
  else if (op == "EQ") {
    Value b = pop();
    Value a = pop();
    push(eq(a, b));
  } else if (op == "NEQ") {
    Value b = pop();
    Value a = pop();
    push(neq(a, b));
  } else if (op == "LT") {
    Value b = pop();
    Value a = pop();
    push(lt(a, b));
  } else if (op == "GT") {
    Value b = pop();
    Value a = pop();
    push(gt(a, b));
  } else if (op == "LE") {
    Value b = pop();
    Value a = pop();
    push(le(a, b));
  } else if (op == "GE") {
    Value b = pop();
    Value a = pop();
    push(ge(a, b));
  }

  // Logical operations
  else if (op == "NOT") {
    Value a = pop();
    push(Value::Int(a.isTruthy() ? 0 : 1));
  } else if (op == "AND") {
    Value b = pop();
    Value a = pop();
    push(Value::Int((a.isTruthy() && b.isTruthy()) ? 1 : 0));
  } else if (op == "OR") {
    Value b = pop();
    Value a = pop();
    push(Value::Int((a.isTruthy() || b.isTruthy()) ? 1 : 0));
  }

  // Control flow
  else if (op == "JMP") {
    ip = labels[arg] - 1; // -1 because ip++ happens after
  } else if (op == "JIF") {
    Value cond = pop();
    if (!cond.isTruthy()) {
      ip = labels[arg] - 1;
    }
  } else if (op == "CALL") {
    push(Value::Int(ip));
    push(Value::Int(fp));
    fp = stack.size();
    ip = labels[arg] - 1;
  } else if (op == "RET") {
    Value ret_val = pop();
    // Discard locals
    while (static_cast<int>(stack.size()) > fp) {
      stack.pop_back();
    }
    // Restore frame pointer and return address
    int old_fp = pop().asInt();
    int ret_addr = pop().asInt();
    // Clean up arguments if specified
    if (!arg.empty()) {
      int num_args = parseIntArg(arg);
      for (int i = 0; i < num_args; i++) {
        stack.pop_back();
      }
    }
    fp = old_fp;
    ip = ret_addr;
    push(ret_val);
  } else if (op == "HALT") {
    ip = code.size(); // Exit
  }

  // String operations
  else if (op == "STRING_NEW") {
    push(Value::String(arg));
  }

  // Data structures
  else if (op == "ARRAY_NEW") {
    int size = pop().asInt();
    int ptr = allocateArray();
    ArrayObject *arr = getArray(ptr);
    arr->elements.resize(size, Value::Int(0));
    push(Value::ArrayPtr(ptr));
  } else if (op == "DICT_NEW") {
    int ptr = allocateDict();
    push(Value::DictPtr(ptr));
  } else if (op == "GET") {
    Value index_or_key = pop();
    Value ptr_or_str = pop();

    if (ptr_or_str.isString()) {
      // String indexing
      int idx = index_or_key.asInt();
      std::string str = ptr_or_str.asString();
      if (idx < 0 || idx >= static_cast<int>(str.length())) {
        error("String index out of range");
      }
      push(Value::String(std::string(1, str[idx])));
    } else if (ptr_or_str.isArrayPtr()) {
      ArrayObject *arr = getArray(ptr_or_str.asHeapPtr());
      int idx = index_or_key.asInt();
      if (idx < 0 || idx >= static_cast<int>(arr->elements.size())) {
        error("Array index out of range");
      }
      push(arr->elements[idx]);
    } else if (ptr_or_str.isDictPtr()) {
      DictObject *dict = getDict(ptr_or_str.asHeapPtr());
      std::string key = index_or_key.asString();
      auto it = dict->pairs.find(key);
      if (it == dict->pairs.end()) {
        error("Key not found: " + key);
      }
      push(it->second);
    }
  } else if (op == "SET") {
    Value val = pop();
    Value index_or_key = pop();
    Value ptr = pop();

    if (ptr.isArrayPtr()) {
      ArrayObject *arr = getArray(ptr.asHeapPtr());
      int idx = index_or_key.asInt();
      if (idx < 0 || idx >= static_cast<int>(arr->elements.size())) {
        error("Array index out of range");
      }
      arr->elements[idx] = val;
    } else if (ptr.isDictPtr()) {
      DictObject *dict = getDict(ptr.asHeapPtr());
      std::string key = index_or_key.asString();
      dict->pairs[key] = val;
    }
  }

  // Built-in functions
  else if (op == "PRINT") {
    builtinPrint();
  } else if (op == "LEN") {
    builtinLen();
  } else if (op == "STR") {
    builtinStr();
  } else if (op == "INT") {
    builtinInt();
  } else if (op == "TYPEOF") {
    builtinTypeof();
  } else if (op == "ABS") {
    builtinAbs();
  } else if (op == "PUSH_NONE") {
    push(Value::None());
  } else if (op == "POP") {
    pop();
  } else if (op == "DUP") {
    push(peek());
  } else if (op == "LOAD") {
    int offset = parseIntArg(arg);
    if (fp + offset >= static_cast<int>(stack.size())) {
      error("Invalid LOAD offset: " + std::to_string(offset));
    }
    push(stack[fp + offset]);
  } else if (op == "STORE") {
    int offset = parseIntArg(arg);
    Value val = pop();
    int idx = fp + offset;
    // Extend stack if necessary
    while (static_cast<int>(stack.size()) <= idx) {
      stack.push_back(Value::Int(0));
    }
    stack[idx] = val;
  }

  // Arithmetic operations
  else if (op == "ADD") {
    Value b = pop();
    Value a = pop();
    push(add(a, b));
  } else if (op == "SUB") {
    Value b = pop();
    Value a = pop();
    push(sub(a, b));
  } else if (op == "MUL") {
    Value b = pop();
    Value a = pop();
    push(mul(a, b));
  } else if (op == "DIV") {
    Value b = pop();
    Value a = pop();
    push(div(a, b));
  }

  // Comparison operations
  else if (op == "EQ") {
    Value b = pop();
    Value a = pop();
    push(eq(a, b));
  } else if (op == "NEQ") {
    Value b = pop();
    Value a = pop();
    push(neq(a, b));
  } else if (op == "LT") {
    Value b = pop();
    Value a = pop();
    push(lt(a, b));
  } else if (op == "GT") {
    Value b = pop();
    Value a = pop();
    push(gt(a, b));
  } else if (op == "LE") {
    Value b = pop();
    Value a = pop();
    push(le(a, b));
  } else if (op == "GE") {
    Value b = pop();
    Value a = pop();
    push(ge(a, b));
  }

  // Logical operations
  else if (op == "NOT") {
    Value a = pop();
    push(Value::Int(a.isTruthy() ? 0 : 1));
  } else if (op == "AND") {
    Value b = pop();
    Value a = pop();
    push(Value::Int((a.isTruthy() && b.isTruthy()) ? 1 : 0));
  } else if (op == "OR") {
    Value b = pop();
    Value a = pop();
    push(Value::Int((a.isTruthy() || b.isTruthy()) ? 1 : 0));
  }

  // Control flow
  else if (op == "JMP") {
    ip = labels[arg] - 1; // -1 because ip++ happens after
  } else if (op == "JIF") {
    Value cond = pop();
    if (!cond.isTruthy()) {
      ip = labels[arg] - 1;
    }
  } else if (op == "CALL") {
    push(Value::Int(ip));
    push(Value::Int(fp));
    fp = stack.size();
    ip = labels[arg] - 1;
  } else if (op == "RET") {
    Value ret_val = pop();
    // Discard locals
    while (static_cast<int>(stack.size()) > fp) {
      stack.pop_back();
    }
    // Restore frame pointer and return address
    int old_fp = pop().asInt();
    int ret_addr = pop().asInt();
    // Clean up arguments if specified
    if (!arg.empty()) {
      int num_args = parseIntArg(arg);
      for (int i = 0; i < num_args; i++) {
        stack.pop_back();
      }
    }
    fp = old_fp;
    ip = ret_addr;
    push(ret_val);
  } else if (op == "HALT") {
    ip = code.size(); // Exit
  }

  // String operations
  else if (op == "STRING_NEW") {
    push(Value::String(arg));
  }

  // Data structures
  else if (op == "ARRAY_NEW") {
    int size = pop().asInt();
    int ptr = allocateArray();
    ArrayObject *arr = getArray(ptr);
    arr->elements.resize(size, Value::Int(0));
    push(Value::ArrayPtr(ptr));
  } else if (op == "DICT_NEW") {
    int ptr = allocateDict();
    push(Value::DictPtr(ptr));
  } else if (op == "GET") {
    Value index_or_key = pop();
    Value ptr_or_str = pop();

    if (ptr_or_str.isString()) {
      // String indexing
      int idx = index_or_key.asInt();
      std::string str = ptr_or_str.asString();
      if (idx < 0 || idx >= static_cast<int>(str.length())) {
        error("String index out of range");
      }
      push(Value::String(std::string(1, str[idx])));
    } else if (ptr_or_str.isArrayPtr()) {
      ArrayObject *arr = getArray(ptr_or_str.asHeapPtr());
      int idx = index_or_key.asInt();
      if (idx < 0 || idx >= static_cast<int>(arr->elements.size())) {
        error("Array index out of range");
      }
      push(arr->elements[idx]);
    } else if (ptr_or_str.isDictPtr()) {
      DictObject *dict = getDict(ptr_or_str.asHeapPtr());
      std::string key = index_or_key.asString();
      auto it = dict->pairs.find(key);
      if (it == dict->pairs.end()) {
        error("Key not found: " + key);
      }
      push(it->second);
    }
  } else if (op == "SET") {
    Value val = pop();
    Value index_or_key = pop();
    Value ptr = pop();

    if (ptr.isArrayPtr()) {
      ArrayObject *arr = getArray(ptr.asHeapPtr());
      int idx = index_or_key.asInt();
      if (idx < 0 || idx >= static_cast<int>(arr->elements.size())) {
        error("Array index out of range");
      }
      arr->elements[idx] = val;
    } else if (ptr.isDictPtr()) {
      DictObject *dict = getDict(ptr.asHeapPtr());
      std::string key = index_or_key.asString();
      dict->pairs[key] = val;
    }
  }

  // Built-in functions
  else if (op == "PRINT") {
    builtinPrint();
  } else if (op == "LEN") {
    builtinLen();
  } else if (op == "STR") {
    builtinStr();
  } else if (op == "INT") {
    builtinInt();
  } else if (op == "TYPEOF") {
    builtinTypeof();
  } else if (op == "ABS") {
    builtinAbs();
  } else if (op == "ARRAY_PUSH") {
    Value val = pop();
    Value ptr = pop();
    ArrayObject *arr = getArray(ptr.asHeapPtr());
    arr->elements.push_back(val);
  } else if (op == "ARRAY_POP") {
    Value ptr = pop();
    ArrayObject *arr = getArray(ptr.asHeapPtr());
    if (arr->elements.empty()) {
      error("Cannot pop from empty array");
    }
    Value val = arr->elements.back();
    arr->elements.pop_back();
    push(val);
  }

  // File I/O
  else if (op == "READFILE") {
    Value filename_val = pop();
    std::string filename = filename_val.asString();
    std::ifstream f(filename);
    if (!f.is_open()) {
      std::string msg = "File not found: " + filename;
      if (!exception_handlers.empty()) {
        auto handler = exception_handlers.back();
        current_exception = msg;
        // Unwind stack
        while (stack.size() > handler.stack_size) {
          stack.pop_back();
        }
        ip = labels[handler.catch_label] - 1;
      } else {
        error(msg);
      }
    } else {
      std::stringstream buffer;
      buffer << f.rdbuf();
      push(Value::String(buffer.str()));
    }
  }

  // Exception handling
  else if (op == "TRY_BEGIN") {
    exception_handlers.push_back({arg, stack.size()});
  } else if (op == "TRY_END") {
    if (!exception_handlers.empty()) {
      exception_handlers.pop_back();
    }
  } else if (op == "THROW") {
    Value error_msg = pop();
    if (!exception_handlers.empty()) {
      auto handler = exception_handlers.back();
      current_exception = error_msg.toString();
      // Unwind stack
      while (stack.size() > handler.stack_size) {
        stack.pop_back();
      }
      ip = labels[handler.catch_label] - 1;
    } else {
      error("Uncaught exception: " + error_msg.toString());
    }
  }

  // Python module support (Mock or Real)
  else if (op == "IMPORT_PYTHON") {
#ifdef PYTHON_SUPPORT
    importPythonModule(arg);
#else
    // Mock: Do nothing
#endif
  } else if (op == "PUSH_MODULE") {
    push(Value::String(arg));
  } else if (op == "GET_ATTR") {
#ifdef PYTHON_SUPPORT
    getPythonAttr(arg);
#else
    // Mock: Handle math.pi
    Value module = pop();
    if (module.asString() == "math" && arg == "pi") {
      push(Value::Float(3.14159265359));
    } else {
      push(Value::None());
    }
#endif
  } else if (op == "CALL_METHOD") {
    // Parse num_args from arg (format: "method_name num_args")
    size_t space_pos = arg.find(' ');
    std::string method_name = arg;
    int num_args = 0;
    if (space_pos != std::string::npos) {
      method_name = arg.substr(0, space_pos);
      num_args = std::stoi(arg.substr(space_pos + 1));
    }

#ifdef PYTHON_SUPPORT
    callPythonMethod(arg, num_args);
#else
    // Mock: Handle math/random methods
    std::vector<Value> args;
    for (int i = 0; i < num_args; i++) {
      args.insert(args.begin(), pop());
    }
    Value module = pop();
    push(mockPythonCall(module.asString(), method_name, args));
#endif
  }

  else {
    error("Unknown opcode: " + op);
  }
}

} // namespace hic
