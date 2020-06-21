#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
import os, sys
import re 

class Lexer(object):

    def getMatcher(self, matcher, current_index, source_code):
        
        if source_code[current_index].count('"') == 2:
            word = source_code[current_index].partition('"')[-1].partition('"'[0])

            if word[2] != '': return [ '"' + word[0] + '"', '', word[2] ]
            else:  return [ '"' + word[0] + '"', '', '' ]
        
        else:
            source_code = source_code[current_index:len(source_code)]

            word = ""
            iter_count = 0
            for item in source_code:
                iter_count += 1
                word += item + " "

                if matcher in item and iter_count != 1: 
                    return [
                        '"' + word.partition('"')[-1].partition('"'[0])[0] + '"', # The string
                        word.partition('"')[-1].partition('"'[0])[2],             # The extra character
                        iter_count - 1                                            # Number of iterations it took to get string
                    ]
                    break
            


    def tokenize(self, source_code):
        KEYWORDS = {"when":"if", "while":"for", "butInCase":'else', "space":"True", "blackhole": "False", "say":"print", "libra":"bool", "virgo":"int", "leo":"str"}
        BUILT_IN_FUNCTIONS = {"say":"print"}
        DATATYPE = {"libra":"bool", "virgo":"int", "leo":"str"}
        tokens = []
        switcher={"Sun":0,
                    "Mercury":1,
                    "Venus":2,
                    "Earth":3,
                    "Mars":4,
                    "Jupiter":5,
                    "Saturn":6,
                    "Uranus":7,
                    "Neptune":8,
                    "Pluto":9}

        source_code = source_code.split()
        source_index = 0 
        while source_index < len(source_code):
            word = source_code[source_index]
            if word in "\n": pass
            elif word in DATATYPE: tokens.append(["DATATYPE", DATATYPE[word]])

            elif word in switcher and source_code[source_index+1] is 'X':
                source_index+=1
                continue

            elif word=="X":
                
                first_el=switcher[source_code[source_index-1]]
                next_index=source_code[source_index+1]
                if next_index[len(next_index)-1]=='.':
                    second_el=switcher[next_index[0:len(next_index)-1]]
                    tokens.append(["INTEGER",str(first_el)+str(second_el)]) 
                    tokens.append(["STATEMENT_END",'.'])
                else:
                    second_el=switcher[source_code[source_index+1]]
                    
                    
                    tokens.append(["INTEGER",str(first_el)+str(second_el)])
                source_index+=1
            elif word in switcher and source_code[source_index+1] is not 'X':tokens.append(["INTEGER",switcher[word]])
          
            elif word == "by":tokens.append(["OPERATOR","+"])
          
            elif word == "landedOn" :tokens.append(["OPERATOR","="])
          
            elif word == "travelTo" : tokens.append(["COMPARISON_OPERATOR", "=="])
          
            elif word == "notTravelTo": tokens.append(["COMPARISON_OPERATOR", "!="])
          
            elif word == "travelFartherThan" : tokens.append(["COMPARISON_OPERATOR",">"])
          
            elif word =="travelUntil": tokens.append(["COMPARISON_OPERATOR", "<"])

            elif word in KEYWORDS: tokens.append(["IDENTIFIER", KEYWORDS[word]])

            elif re.match("[a-z]", word) or re.match("[A-Z]", word): 
                if word[len(word) - 1] != ';': 
                    tokens.append(["IDENTIFIER", word])
                else: 
                    tokens.append(["IDENTIFIER", word[0:len(word) - 1]])

            elif word in "*-/+%=": tokens.append(["OPERATOR", word])

            elif word == "&&" or word == "||": tokens.append(["BINARY_OPERATOR", word])

            elif word == "§": tokens.append(["SEPERATOR", word])

            elif word in "{}": tokens.append(["SCOPE_DEFINER", word])

            
            elif ('"') in word: 

                matcherReturn = self.getMatcher('"', source_index, source_code)

                if matcherReturn[1] == '': tokens.append(["STRING", matcherReturn[0]])

                else:

                   
                    tokens.append(["STRING", matcherReturn[0] ])
                    
                    if '.' in matcherReturn[1]: tokens.append(["STATEMENT_END", "."])

                    source_index += matcherReturn[2]

                    pass

            if "." in word[len(word) - 1]: 
               
                tokens.append(["STATEMENT_END", "."])

            source_index += 1
        
        return tokens
