#include "vm.hpp"
#include <iostream>

int main(int argc, char *argv[]) {
  if (argc < 2) {
    std::cerr << "Usage: hic_vm <program.asm>" << std::endl;
    return 1;
  }

  try {
    hic::VM vm;
    vm.loadProgram(argv[1]);
    vm.run();
    return 0;
  } catch (const std::exception &e) {
    std::cerr << "Fatal error: " << e.what() << std::endl;
    return 1;
  }
}
