/*
    Basic Type:

    (1) Integer
        Regex: ^-?[1-9][0-9]*$|^0$
        Example: 0
        Remarks:
            1. Max Value: 9223372036854775806 (long long)
            2. Min Value: -9223372036854775806 (long long)

    (2) Float
        Regex: ^-?[0-9]+\.[0-9]+$
        Example: 0.0, -1.23, ...
        Remarks:
            1. Max Value: 9223372036854775806.0 (long long)
            2. Min Value: -9223372036854775806.0 (long long)

    (3) String
        Regex: ^\".*\"$
        Example: "asd"
        Remarks:
            1. A string must stats and ends with quotation mark (").
            2. A string needs to handle escape char.
            3. An escape char always starts with reverse slash (\).
            4. Any char after reverse slash will be handled as a string.
               (For example, "A \" B" will be handled as 'A " B'.)

    (4) Boolean
        Regex: true|false|null
        Remarks:
            1. The type of null is bool.
            2. The integer value of true, false, and null are 1, 0, -1 respectively.
            3. The bool value of integer is true if greater than 1; false if 0; null if less than -1.

    (5) Character
        Regex: '.'
        Remarks:
            1. Char must be actually one char.
            2. Char cannot be empty.
*/

/*
    Special Type:

    (1) list
        Regex: [<value> (, <value>...)]
        Example: [1, "a", true]
        Remarks:
            1. List can store not just one type of value, but can store multi-types of values.

    (2) Dict
        Regex: {<key>: <value> (, <key>: <value>...)}
        Example: {"name": "HyLang", "type": "programming language"}
        Remarks:
            1. Value of Key must be hashable (for example, int, string, etc.).
*/

/*
    Special Built-In Values:

    (1) INF
        Type: Integer
        Value: 9223372036854775807 (long long)
        Description:
            1. Any int or float is less than INF.
            2. Any int or float greater than 9223372036854775806 is INF.
            3. INF is equal to INF.

    (2) Division By Zero
        Type: Integer
        Value: INF
        Description:
            1. Any int or float dividing by zero is INF.
*/

/*
    Type Convertion:

    (1) Integer
        1. int(int): return int.
        2. int(float): return all digits before the dot (.).
        3. int(string): <ERROR>
        4. int(bool): return 1, 0, or -1 if bool is true, false, or null respectively.
        5. int(char): return ascii code of int.

    (2) Float
        1. float(int): return float.
        2. float(float): return falot.
        3. float(string): <ERROR>
        4. float(bool): float(int(bool))
        5. float(char) float(int(char))

    (3) String
        1. string(int): return string.
        2. string(float): return string.
        3. string(string): return string.
        4. string(bool): return "true", "false", or "null".
        5. string(char): return string.

    (4) Boolean
        1. bool(int): return true if int is 1 or greater than 1; false if int is 0; null if int is -1 or less than -1.
        2. bool(float): return bool(int(float)).
        3. bool(string): return true if string is not empty; otherwise false.
        4. bool(bool): return bool.
        5. bool(char): return true.
*/

/*
    Basic Operator:

    (1) Addition (+)
        1. int + int = int
        2. int + float = float(int) + float
        3. int + string = string(int) + string
        4. int + bool = int + int(bool)
        5. int + char = int + int(char)

        6. float + int = float + float(int)
        7. float + float = float
        8. float + string = string(float) + string
        9. float + bool = float + float(int(bool))
        10. float + char = float + float(int(char))

        11. string + int = string + string(int)
        12. string + float = string + string(float)
        13. string + string = string
        14. string + bool = string + string(bool)
        15. string + char = string + string(bool)

        16. bool + int = int(bool) + int
        17. bool + float = float(int(bool)) + float
        18. bool + string = string(bool) + string
      * 19. bool + bool = bool(int(bool) + int(bool))
      * 20. bool + char = true

    (2) Subtraction (-)
        1. int - int = int
        2. int - float = float(int) - float
        3. int - string = <ERROR>
        4. int - bool = int - int(bool)
        5. int - char = int - int(char)

        6. float - int = float - float(int)
        7. float - float = float
        8. float - string = <ERROR>
        9. float - bool = float - float(int(bool))
        10. float - char = float - float(int(char))

        11. string - int = <ERROR>
        12. string - float = <ERROR>
        13. string - string = <ERROR>
        14. string - bool = <ERROR>
        15. string - char = <ERROR>

        16. bool - int = int(bool) - int
        17. bool - float = float(int(bool)) - float
        18 bool - string = <ERROR>
      * 19. bool - bool = bool(int(bool) - int(bool))
      * 20. bool - char = false

    (3) Multiplication (*)
        1. int * int = int
        2. int * float = float(int) * float
        3. int * string = <ERROR>
        4. int * bool = int * int(bool)
        5. int * char = int * int(char)

        6. float * int = float * float(int)
        7. float * float = float
        8. float * string = <ERROR>
        9. float * bool = float * float(int(bool))
        10. float * char = float * float(int(char))

      * 11. string * int = string repeat int times if int is 1 or greater than 1; empty string ("") if int is 0 or less than 0
        12. string * float = <ERROR>
        13. string * string = <ERROR>
      * 14. string * bool = string * int(bool)
      * 15. string * char = <ERROR>

        16. bool * int = int(bool) * int
        17. bool * float = float(int(bool)) * float
        18. bool * string = <ERROR>
      * 19. bool * bool = bool(int(bool) * int(bool))
      * 20. bool - char = <ERROR>

    (4) Division (/)
        1. int / int = int
        2. int / float = float(int) - float
        3. int / string = <ERROR>
        4. int / bool = int / int(bool)
        5. int / char = int / int(char)

        5. float / int = float / float(int)
        6. float / float = float
        7. float / string = <ERROR>
        8. float / bool = float / float(int(bool))
        8. float / char = float / float(int(char))

        9. string / int = <ERROR>
        10. string / float = <ERROR>
        11. string / string = <ERROR>
        12. string / bool = <ERROR>
        12. string / char = <ERROR>

        13. bool / int = int(bool) / int
        14. bool / float = float(int(bool)) / float
        15. bool / string = <ERROR>
      * 16. bool / bool = bool(int(bool) / int(bool))
      * 20. bool / char = <ERROR>

    (5) Exponentiation (**)
        1. int ** int = int
        2. int ** float = float(int) ** float
        3. int ** string = <ERROR>
        4. int ** bool = int ** int(bool)
        5. int ** char = int ** int(char)

        6. float ** int = float ** float(int)
        7. float ** float = float
        8. float ** string = <ERROR>
        9. float ** bool = float ** float(int(bool))
        10. float ** char = float ** float(int(char))

      * 11. string ** int = <ERROR>
        12. string ** float = <ERROR>
        13. string ** string = <ERROR>
      * 14. string ** bool = <ERROR>
      * 15. string ** char = <ERROR>

        16. bool ** int = int(bool) ** int
        17. bool ** float = float(int(bool)) ** float
        18. bool ** string = <ERROR>
      * 19. bool ** bool = bool(int(bool) ** int(bool))
      * 20. bool ** char = <ERROR>

    (6) Remainder (%)
        1. int % int = int
        2. int % float = float
        3. int % string = <ERROR>
        4. int % bool = int % int(bool)
        5. int % char = int % int(char)

        6. float % int = float % float(int)
        7. float % float = float
        8. float % string = <ERROR>
        9. float % bool = float % float(int(bool))
        10. float % bool = float % float(int(char))

        11. string % int = <ERROR>
        12. string % float = <ERROR>
        13. string % string = <ERROR>
        14. string % bool = <ERROR>
        15. string % char = <ERROR>

        16. bool % int = int(bool) % int
        17. bool % float = float(int(bool)) % float
        18. bool % string = <ERROR>
      * 19. bool % bool = bool(int(bool) % int(bool))
      * 20. bool % char = <ERROR>

    (6) Bit Left Shift (<<)
        1. int << int = int
        2. int << float = int << int(float)
        3. int << string = <ERROR>
        4. int << bool = int << int(bool)
        5. int << char = int << int(char)

        6. float << int = float(int(float) << int)
        7. float << float = float(int(float) << int(float))
        8. float << string = <ERROR>
        9. float << bool = float(int(float) << int(bool))
        10. float << char = float(int(float) << int(char))

      * 11. string << int = remove the first n (int) chars from string
        12. string << float = <ERROR>
        13. string << string = <ERROR>
        14. string << bool = <ERROR>
        15. string << char = <ERROR>

        16. bool << int = int(bool) << int
        17. bool << float = int(bool) << int(float)
        18. bool << string = <ERROR>
      * 19. bool << bool = bool(int(bool) << int(bool))
      * 20. bool << char = <ERROR>

    (7) Bit Right Shift (>>)
        1. int >> int = int
        2. int >> float = int >> int(float)
        3. int >> string = <ERROR>
        4. int >> bool = int >> int(bool)
        5. int >> char = int >> int(char)

        6. float >> int = float(int(float) >> int)
        7. float >> float = float(int(float) >> int(float))
        8. float >> string = <ERROR>
        9. float >> bool = float(int(float) >> int(bool))
        10. float >> char = float(int(float) >> int(char))

        11. string >> int = remove the last n (int) chars from string
        12. string >> float = <ERROR>
        13. string >> string = <ERROR>
        14. string >> bool = <ERROR>
        15. string >> char = <ERROR>

        16. bool >> int = int(bool) >> int
        17. bool >> float = int(bool) >> int(float)
        18. bool >> string = <ERROR>
      * 19. bool >> bool = bool(int(bool) >> int(bool))
      * 19. bool >> char = <ERROR>

    (8) Bit AND (&)
        1. int & int = int
        2. int & float = int & int(float)
        3. int & string = <ERROR>
        4. int & bool = int & int(bool)
        5. int & char = int & int(char)

        6. float & int = float(int(float) & int)
        7. float & float = float(int(float) & int(float))
        8. float & string = <ERROR>
        9. float & bool = float(int(float) & int(bool))
        10. float & char = float(int(float) & int(char))

        11. string & int = <ERROR>
        12. string & float = <ERROR>
        13. string & string = <ERROR>
        14. string & bool = <ERROR>
        15. string & char = <ERROR>

        16. bool & int = int(bool) & int
        17. bool & float = int(bool) & int(float)
        18. bool & string = <ERROR>
      * 19. bool & bool = bool(int(bool) & int(bool))
        20. bool & char = <ERROR>

    (8) Bit OR (|)
        1. int | int = int
        2. int | float = int | int(float)
        3. int | string = <ERROR>
        4. int | bool = int | int(bool)

        5. float | int = int(float) | int
        6. float | float = int(float) | int(float)
        7. float | string = <ERROR>
        8. float | bool = int(float) | int(bool)

        9. string | int = <ERROR>
        10. string | float = <ERROR>
        11. string | string = <ERROR>
        12. string | bool = <ERROR>

        13. bool | int = int(bool) | int
        14. bool | float = int(bool) | int(float)
        15. bool | string = <ERROR>
      * 16. bool | bool = bool(int(bool) | int(bool))

    (10) Bit XOR (^)
        1. int ^ int = int
        2. int ^ float = int ^ int(float)
        3. int ^ string = <ERROR>
        4. int ^ bool = int ^ int(bool)

        5. float ^ int = int(float) ^ int
        6. float ^ float = int(float) ^ int(float)
        7. float ^ string = <ERROR>
        8. float ^ bool = int(float) ^ int(bool)

        9. string ^ int = <ERROR>
        10. string ^ float = <ERROR>
        11. string ^ string = <ERROR>
        12. string ^ bool = <ERROR>

        13. bool ^ int = int(bool) ^ int
        14. bool ^ float = int(bool) ^ int(float)
        15. bool ^ string = <ERROR>
      * 16. bool ^ bool = bool(int(bool) ^ int(bool))

    (11) Logical AND (and)
        1. int and int = bool(int) and bool(int)
        2. int and float = bool(int) and bool(int(float))
        3. int and string = bool(int) and bool(string)
        4. int and bool = bool(int) and bool

        5. float and int = bool(int(float)) and bool(int)
        6. float and float = bool(int(float)) and bool(int(float))
        7. float and string = bool(int(float)) and bool(string)
        8. float and bool = bool(int(float)) and bool

        9. string and int = bool(string) and bool(int)
        10. string and float = bool(string) and bool(int(float))
        11. string and string = bool(string) and bool(string)
        12. string and bool = bool(string) and bool

        13. bool and int = bool and bool(int)
        14. bool and float = bool and bool(int(float))
        15. bool adn string = bool and bool(string)
      * 16. bool and bool = bool and bool

    (12) Logical OR (or)
        1. int or int = bool(int) or bool(int)
        2. int or float = bool(int) or bool(int(float))
        3. int or string = bool(int) or bool(string)
        4. int or bool = bool(int) or bool

        5. float or int = bool(int(float)) or bool(int)
        6. float or float = bool(int(float)) or bool(int(float))
        7. float or string = bool(int(float)) or bool(string)
        8. float or bool = bool(int(float)) or bool

        9. string or int = bool(string) or bool(int)
        10. string or float = bool(string) or bool(int(float))
        11. string or string = bool(string) or bool(string)
        12. string or bool = bool(string) or bool

        13. bool or int = bool or bool(int)
        14. bool or float = bool or bool(int(float))
        15. bool adn string = bool or bool(string)
      * 16. bool or bool = bool or bool

    (13) Logical NOT (not)
        1. not int = not bool(int)
        2. not float = not bool(int(float))
        3. not string = not bool(string)
        4. not bool = not bool
      * 5. not bool = false

    (14) Other Operators
        1. ++   (add 1 to self)
        2. --   (sub 1 from self)
        3. !=   (not equal)
        4. ==   (equal)
        5. >    (greater than)
        6. <    (less than)
        7. >=   (equal or greater than)
        8. <=   (equal or less than)
        9. @    (get address of variable)
        10. @@  (get variavle value from address)
*/

/*
    Assignment:

    (1) =    (assignment)
    (2) >=   (equal or greater than)
    (3) <=   (equal or less than)
    (4) +=   (self add)
    (5) -=   (self sub)
    (6) *=   (self mul)
    (7) /=   (self div)
    (8) **=  (self exp)
    (9) >>=  (self bit left shift)
    (10) <<= (self bit right shift)
*/

/*
    Declaration:

    (1) Integer

        int VARIABLE; // Declarating without value.
                      // Initial value: 0

        int VARIABLE = 0; // Declarating with value.

    (2) Float

        float VARIABLE; // Declarating without value.
                        // Initial value: 0.0

        float VARIABLE = 0.0; // Declaration with value.

    (3) String

        string VARIABLE; // Declarating without value.
                         // Initial value: ""

        string VARIABLE = ""; // Declaration with value.

    (4) Boolean

        bool VARIABLE; // Declarating without value.
                       // Initial value: false

        bool VARIABLE = true; // Declaration with value.
*/

/*
    If-Else Statement:

    (1) if
        Grammar:
            if (<condition>) {
                ...
            }

    (2) else if / elseif / elif
        Grammar:
            else if (<condition>) {
                ...
            }

    (3) else
        Grammar:
            else {
                ...
            }
*/

/*
    For-Loop Statement:

    for (<initialization>;<continue condition>;<action>) {
        ...
    }
*/

/*
    While Statement:

    while (<condition>) {
        ...
    }
*/

/*
    Function Statement:

    function (<initialization>) {
        ...
        return <value>;
    }
*/

/*
    Built-In Functions:

    (1) print()
        Description:
            Function print() is used to print text to the screen.
            Using comma (,) to print multiple texts.

        Parameters:
            1. int, float , string or bool values.

        Returns:
            1. Show texts on the screen.
            2. Returns 0;

    (2) input()
        Description:
            Function input() is used to get cli input from user.

        Parameters:
            1. No parameters input.

        Returns:
            1. Return a inputed string value.

    (3) length()
        Description:
            Function length() is used to get the length of string, list, or dict.

        Parameters:
            1. A string, list, or dict value.

        Returns:
            1. Return a int value of length.
*/