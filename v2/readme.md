一、簡介：

最近試著自己做了一個超微型程式語言，那就讓我們先來介紹它的語法吧～
這個程式語言提供了幾個基本的語法，包括：

1. var (宣告變數)

使用 var x = b 宣告變數，變數型態有 int、float、string，以及 array。
範例：
    var myName = 'test'
    var age = 123
    var score = 10.5
    var sports = ['run', 'dance', 'stroll']

2. if() ... endif

使用 if() ... endif 判斷條件，條件僅接受簡單的 > 和 <（原諒它就只是個超微型語言...），沒有 else 語法。
範例：

    var age = 123
    if(age > 100)
        print('なに！')
    endif

    # output:
    # なに！

3. for() ... endfor

使用 for() ... endfor 進行重複動作。
語法
    for(<condition>; <opretion>)
    <condition> 僅接受 > 或 <
    <opretion> 僅接受 += 或 -=

範例：

    var a = 1
    for(a < 5;a += 1)
        print(a)
    endfor

    # output:
    # 1
    # 2
    # 3
    # 4

4. print()

使用 print() ...，不然你還能拿 print 做什麼...
範例：

    var a = 'test'
    print(a)
    # output:
    # test

    print(1, 2, 'asd')
    # output:
    # 1
    # 2
    # asd

5. #

使用 # 來註解程式
範例：

    # Hi from HIC

二、範例程式

簡單的 print 1 to 100 的範例：

    var a = 1

    for(a < 101; a += 1)
        print(a)
    endfor

    # output:
    # 1
    # 2
    # .
    # .
    # .
    # 100

簡單的雙迴圈範例 print 5 'aaaaa' for 10 times：

    var a = 0

    for(a < 10; a += 1)
        var b = 0

        for(b < 5; b += 1)
            print('aaaaa')
        endfor

    endfor

簡單 print、if 搭配範例：

    var a = 1

    for(a < 10; a += 1)
        if(a > 5)
            print(a)
        endif
    endfor

    # output:
    # 6
    # 7
    # 8
    # 9
    # 10


三、原理：

    這個程式語言的執行分成兩個步驟：(1) 將程式語言轉為 assembly（2 pass）；(2) 執行 assembly。
    這個 Assembler 不會進行 lexical analysis，只會做簡單的 syntactic analysis。

    第一步：將程式語言轉為 assembly
        使用 assembler v2.py 將程式語言轉為 assembly。Assmbly 的設計參考 SIC/XE。其他細節可以在 Github 上的原始碼內找到
        使用方法：python '.\assembler v2.py' '.\test v2.pi' '.\obj code v2.hic'
        test v2.pi 是指定 input file
        obj code v2.hic 是指定 output file（組譯出來的組合語言就在這裡）

    第二步：執行 assembly
        使用 excuter v2.py 執行 .hic 檔，來模擬 assembly 的執行。
        使用方法：python '.\executer v2.py' '.\obj code v2.hic'
        obj code v2.hic 是指定 input file

    讓我們看看剛才的簡單範例（print 1 to 100）。高階程式碼如下：
        var a = 1

        for(a < 101; a += 1)
            print(a)
        endfor

    組譯出來的 hic code 如下：
        VAL $a 1
        LAB DRMDKQKKAI # DRMDKQKKAI is a random string
        MSG $a
        ADD $a 1
        JLT $a 101 DRMDKQKKAI

四、其他

    Github : https://github.com/91d906h4/HIC
    Required Python version : >= 3.10
    Required packages : os, sys, random, string