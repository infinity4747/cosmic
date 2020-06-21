#!/usr/local/bin/python3
# -*- coding: utf-8 -*- c

import os
import sys
import lexer
import parser
import objgen

def main():
    
    content  = ""          
    path     = os.getcwd()  

    
    try: fileName = sys.argv[1]
    except:
        print("[ERROR] Expected 1 Argument Containing File Name to be Run e.g 'tachyon main.tn'")
        return

   
    if fileName[len(fileName) - 3:len(fileName)] != ".cosmix":
        print("[ERROR] File extension not recognised please make sure extension is '.tn'")
        return 

    try:
        print('[ERROR] Expected 1 argument found 2 (' + sys.argv[1] + ", " + sys.argv[2] + ')')
        return # quit programme
    except: pass

    # Open source code file and get it's content and save it to the 'contents' var
    try:
        with open(path + "/" + fileName, "r") as file:
            content = file.read()
    except: 
        print('Cannot find "' + fileName + '"')
    

    print('LEXER LOG \n')
  
    lex = lexer.Lexer()

    
    tokens = lex.tokenize(content)
    print(tokens)

  

    print('  PARSER LOG \n')
    Parser = parser.Parser(tokens)
    source_ast = Parser.parse(tokens)
    print(source_ast)
   
   
    print('  OBJECT GENERATION LOG   \n')
    object_generator = objgen.ObjectGenerator(source_ast)

    exec_string = object_generator.object_definer(False)
    

    print(' TRANSPILED CODE  \n')
    print(exec_string)
    print('\n')

    print('OUTPUT  \n')
    exec(exec_string)
    print('\n| \n')

main()

