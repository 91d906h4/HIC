// This is a comment
/*
    This is also the comment
*/

// .hy is our language's extension
// We can use #import to import the functions from other file
#import "math.hy"
#import "path/is/also/ok.hy"

// data types: var, func
// var can be a string, char, int, float, array (list), dict, etc.
// func is function, and we can consider it as a "executable var"
// like C, we use main as the entry point
func main() {
    var nothing; // null if not given values
    var my_array = [1, "hi", null, main]; // use [] to represent array
    var my_dict = {0: "0", 1: "1", "2": 2}; // use {} to represent dict
    return null; // func must return something
}