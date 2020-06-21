#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
import os, sys



class Parser(object):

    KEYWORDS = [ "if", "for", "else", "True", "False", "print", "bool", "int", "str"]
    DATATYPE = ["bool", "int", "str"]
    BUILT_IN_FUNCTIONS=["print"]
    def __init__(self, token_stream):
        
        self.source_ast = { 'main_scope': [] }
        
        self.symbol_tree = []
     
        self.token_stream = token_stream
     
        self.token_index = 0


    def parse(self, token_stream):
        
        KEYWORDS = [ "if", "for", "else", "True", "False", "print", "bool", "int", "str"]
        DATATYPE = ["bool", "int", "str"]
        BUILT_IN_FUNCTIONS=["print"]
        
        while self.token_index < len(token_stream):

            
            token_type = token_stream[self.token_index][0]
            token_value = token_stream[self.token_index][1]

        
            if token_type == "DATATYPE":
                self.variable_decleration_parsing(token_stream[self.token_index:len(token_stream)], False)
                
           
            elif token_type == "IDENTIFIER" and token_value == "if":
                self.conditional_statement_parser(token_stream[self.token_index:len(token_stream)], False)


            elif token_type == "IDENTIFIER" and token_value == "for":
                print("FOR BEFORE: ", self.token_index)
                self.parse_for_loop(token_stream[self.token_index:len(token_stream)], False)
                print("FOR AFTER: ", self.token_index)

          
            elif token_type == "IDENTIFIER" and token_value in BUILT_IN_FUNCTIONS:
                self.parse_built_in_function(token_stream[self.token_index:len(token_stream)], False)

            self.token_index += 1

        return self.source_ast


    def parse_for_loop(self, token_stream, isInBody):
    

        ast = {'ForLoop': []}
        
        tokens_checked = 1
        # 1 - ConditionForLoop
        # 2 - IncrementerForLoop
        loopSection = 1

       
        while tokens_checked < len(token_stream):

           
            if token_stream[tokens_checked][1] == '{': break
            
           
            if tokens_checked == 1:

                
                var_decl_tokens = self.get_token_to_matcher("§", '{', token_stream[tokens_checked:len(token_stream)])

                
                if var_decl_tokens == False:
                    self.send_error_message("Loop missing seperator '§'", token_stream)

                var_decl_tokens[0].append(['STATEMENT_END', '.'])
                var_parsing = self.variable_decleration_parsing(var_decl_tokens[0], True)
                ast['ForLoop'].append( { 'initialValueName': var_parsing[0]['VariableDecleration'][1]['name'] })
                ast['ForLoop'].append( { 'initialValue': var_parsing[0]['VariableDecleration'][2]['value'] })
                self.token_index -= var_decl_tokens[1]

            if token_stream[tokens_checked][1] == '§':
                if loopSection == 1:
                    condition_tokens = self.get_token_to_matcher('§', '{', token_stream[tokens_checked + 1:len(token_stream)])
                    ast['ForLoop'].append({ 'comparison': condition_tokens[0][1][1] })
                    ast['ForLoop'].append({ 'endValue': condition_tokens[0][1][1] })
                    tokens_checked += condition_tokens[1]

                if loopSection == 2:
                    increment_tokens = self.get_token_to_matcher('{', '}', token_stream[tokens_checked + 1:len(token_stream)])
                    ast['ForLoop'].append({ 'incrementer': self.assemble_token_values(increment_tokens[0]) })
                    tokens_checked += increment_tokens[1]

              
                loopSection += 1

            
            tokens_checked += 1

        self.token_index += tokens_checked

        
        get_body_tokens = self.get_statement_body(token_stream[tokens_checked + 1:len(token_stream)])

      
        if not isInBody: 
            self.parse_body(get_body_tokens[0], ast, 'ForLoop', False)
        else: 
            self.parse_body(get_body_tokens[0], ast, 'ForLoop', True)

      
        tokens_checked += get_body_tokens[1]

        return [ast, tokens_checked]


    def assemble_token_values(self, tokens):
        attached_tokens = ""
        for token in tokens:
            attached_tokens += str(token[1]) + ""
        return attached_tokens


    def get_token_to_matcher(self, matcher, terminating_matcher, token_stream):
  

        tokens = []
        tokens_checked = 0

        for token in token_stream:
            tokens_checked += 1
            if token[1] == terminating_matcher: return False
            if token[1] == matcher:
                return [tokens, tokens_checked - 1]
            else: 
                tokens.append(token)

       
        return False




    def parse_built_in_function(self, token_stream, isInBody):
        ast = {'PrebuiltFunction': []}
        tokens_checked = 0


        for token in range(0, len(token_stream)):

           
            if token_stream[token][0] == "STATEMENT_END": break
            
            if token == 0:
                ast['PrebuiltFunction'].append( {'type': token_stream[token][1]} )
                
            # This will get the parameter
            if token == 1 and token_stream[token][0] in ['INTEGER', 'STRING', 'IDENTIFIER']:

                # If the argument passed is a variable (identifier) then try get value
                if token_stream[token][0] == 'IDENTIFIER':
                    # Get value and handle any errors
                    value = self.get_variable_value(token_stream[token][1])
                    if value != False: 
                        ast['PrebuiltFunction'].append( {'arguments': [value]} )
                    else: 
                        self.send_error_message("Variable '%s' does not exist" % token_stream[tokens_checked][1], token_stream[0:tokens_checked + 1])
                else:
                    if token_stream[token + 1][0] == 'STATEMENT_END':
                        ast['PrebuiltFunction'].append( {'arguments': [token_stream[token][1]]} )
                    else:
                        value_list_func_call = self.form_value_list(token_stream[tokens_checked:len(token_stream)])
                        print(value_list_func_call)

            # This will throw an error if argument passed in is not a permitted token type 
            elif token == 1 and token_stream[token][0] not in ['INTEGER', 'STRING', 'IDENTIFIER']: 
                self.send_error_message("Invalid argument type of %s expected string, identifier or primitive data type" % token_stream[token][0], 
                                              token_stream[0:tokens_checked + 1])

            tokens_checked += 1 

       
        if not isInBody: self.source_ast['main_scope'].append(ast)
      
        self.token_index += tokens_checked

        return [ast, tokens_checked]


    
    def variable_decleration_parsing(self, token_stream, isInBody):
        
        ast = { 'VariableDecleration': [] }  
        tokens_checked = 0                  
        var_exists = True

        for x in range(0, len(token_stream)):

          
            token_type = token_stream[x][0]
            token_value = token_stream[x][1]

            
            if x == 2 and token_type == "OPERATOR" and token_value == "=":
                pass
            
            if x == 2 and token_type != "OPERATOR" and token_value != "=":
                self.send_error_message("Variable Decleration Missing '='.", self.token_stream[self.token_index:self.token_index + tokens_checked + 2])

          
            if token_stream[x][0] == "STATEMENT_END": break

          
            if x == 0: ast['VariableDecleration'].append({ "type": token_value })

           
            if x == 1 and token_type == "IDENTIFIER":
                
                
                if self.get_variable_value(token_value) != False:
                    self.send_error_message("Variable '%s' already exists and cannot be defined again!" % token_value, self.token_stream[self.token_index:self.token_index + tokens_checked + 1])
                else:
                   
                    var_exists = False

                   
                    if token_stream[x + 1][0] == "STATEMENT_END":
                       
                        ast['VariableDecleration'].append({ "name": token_value })
                        ast['VariableDecleration'].append({ "value": '"undefined"' })
                        tokens_checked += 1
                        break
                    else:
                        ast['VariableDecleration'].append({ "name": token_value })

          
            if x == 1 and token_type != "IDENTIFIER":
                self.send_error_message("Invalid Variable Name '%s'" % token_value, self.token_stream[self.token_index:self.token_index + tokens_checked + 1] )

           
            if x == 3 and token_stream[x + 1][0] == "STATEMENT_END":


                print(int(token_value))
                try: ast['VariableDecleration'].append({ "value": int(token_value) })
                try:
                    ast['VariableDecleration'].append({ "value": int(token_value) })
                except ValueError: ast['VariableDecleration'].append({ "value": bool(token_value) })
                else:
                     ast['VariableDecleration'].append({ "value": token_value })    
                
                   
            # This will parse any variable declerations which have concatenation or arithmetics
            elif x >= 3:

                # This will call the form_value_list method and it will return the concatenation value and tokens checked
                value_list_func_call = self.form_value_list(token_stream[tokens_checked:len(token_stream)])
                value_list = value_list_func_call[0]
                tokens_checked += value_list_func_call[1]

                # Call the equation parser and append value returned or try concat parser if an error occurs
                try: 
                    ast['VariableDecleration'].append({ "value": self.equation_parser(value_list)})
                except:
                    try: 
                        ast['VariableDecleration'].append({ "value": self.concatenation_parser(value_list) })
                    except: 
                        self.send_error_message("Invalid variable decleration!", self.token_stream[self.token_index:self.token_index + tokens_checked] )
                break  # Break out of the current var parsing loop since we just parsed everything

            tokens_checked += 1  # Indent within overall for loop
        print(ast["VariableDecleration"])
        # Last case error validation checking if all needed var decl elements are in the ast such as:
        # var type, name and value
        try: ast['VariableDecleration'][0] 
        except: self.send_error_message("Invalid variable decleration could not set variable type!", self.token_stream[self.token_index:self.token_index + tokens_checked] )
        try: ast['VariableDecleration'][1]
        except: self.send_error_message("Invalid variable decleration could not set variable name!", self.token_stream[self.token_index:self.token_index + tokens_checked] )
        try: ast['VariableDecleration'][2]
        except: self.send_error_message("Invalid variable decleration could not set variable value!", self.token_stream[self.token_index:self.token_index + tokens_checked] )

        # If this is being run to parse inside a body then there is no need to add it to the source ast
        # as it will be added to the body of statement being parsed
        if not isInBody:
            self.source_ast['main_scope'].append(ast)

        if not var_exists:
            self.symbol_tree.append( [ast['VariableDecleration'][1]['name'], ast['VariableDecleration'][2]['value']] )

        self.token_index += tokens_checked

        return [ast, tokens_checked] # Return is only used within body parsing to create body ast




    def conditional_statement_parser(self, token_stream, isNested):
        

        tokens_checked = 0
        ast = {'ConditionalStatement': []}

        for x in range(0, len(token_stream)):

            tokens_checked += 1
            token_type  = token_stream[x][0]
            token_value = token_stream[x][1]
            allowed_conditional_token_types = ['INTEGER', 'STRING', 'IDENTIFIER']

            if token_type == 'SCOPE_DEFINER' and token_value == '{': break

            if token_type == 'IDENTIFIER' and  token_value == 'if':  pass

            if x == 1 and token_type in allowed_conditional_token_types:
                if self.get_variable_value(token_value) != False:
                    ast['ConditionalStatement'].append( {'value1': self.get_variable_value(token_value)} )
                else:
                    ast['ConditionalStatement'].append( {'value1': token_value} )

            if x == 2 and token_type == 'COMPARISON_OPERATOR':
                ast['ConditionalStatement'].append( {'comparison_type': token_value} )

            if x == 3 and token_type in allowed_conditional_token_types:
                if self.get_variable_value(token_value) != False:
                    ast['ConditionalStatement'].append( {'value2': self.get_variable_value(token_value)} )
                else:
                    ast['ConditionalStatement'].append( {'value2': token_value} )

        self.token_index += tokens_checked - 1

        get_body_return = self.get_statement_body(token_stream[tokens_checked:len(token_stream)])

        
        if isNested == True: 
            self.parse_body(get_body_return[0], ast, 'ConditionalStatement', True)
        else: 
            self.parse_body(get_body_return[0], ast, 'ConditionalStatement', False)

        tokens_checked += get_body_return[1]

        return [ast, tokens_checked] # Return is only used within body parsing to create body ast



    def parse_body(self, token_stream, statement_ast, astName, isNested):
   
        KEYWORDS = [ "if", "for", "else", "True", "False", "print", "bool", "int", "str"]
        DATATYPE = ["bool", "int", "str"]
        BUILT_IN_FUNCTIONS=["print"]
        ast = {'body': []}
        tokens_checked = 0
        nesting_count = 0

        while tokens_checked < len(token_stream):

            if token_stream[tokens_checked][0] == "DATATYPE":
                var_decl_parse = self.variable_decleration_parsing(token_stream[tokens_checked:len(token_stream)], True)
                ast['body'].append(var_decl_parse[0])
                tokens_checked += var_decl_parse[1]

            # This will parse nested conditional statements within the body
            elif token_stream[tokens_checked][0] == 'IDENTIFIER' and token_stream[tokens_checked][1] == 'if':
                condition_parsing = self.conditional_statement_parser(token_stream[tokens_checked:len(token_stream)], True)
                ast['body'].append(condition_parsing[0])
                tokens_checked += condition_parsing[1] - 1 # minus one to not skip extra token

            elif token_stream[tokens_checked][0] == "IDENTIFIER" and token_stream[tokens_checked][1] == "for":
                loop_parse = self.parse_for_loop(token_stream[tokens_checked:len(token_stream)], True)
                ast['body'].append(loop_parse[0])
                tokens_checked += loop_parse[1]

            # This will parse builtin functions within the body 
            elif token_stream[tokens_checked][0] == 'IDENTIFIER' and token_stream[tokens_checked][1] in BUILT_IN_FUNCTIONS:
                built_in_func_parse = self.parse_built_in_function(token_stream[tokens_checked:len(token_stream)], True)
                ast['body'].append(built_in_func_parse[0])
                tokens_checked += built_in_func_parse[1]


            # This is needed to increase token index by 1 when a closing scope definer is found because it is skipped
            # so when it is found then add 1 or else this will lead to a logical bug in nesting
            if token_stream[tokens_checked][1] == '}':
                nesting_count += 1

            tokens_checked += 1

        self.token_index += nesting_count + 1
        # Form the full ast with the statement and body combined and then add it to the source ast
        statement_ast[astName].append(ast)
        # If the statments is not nested then add it or else don;t because parent will be added containing the child
        if not isNested: self.source_ast['main_scope'].append(statement_ast) 



    def get_statement_body(self, token_stream):
       
        nesting_count = 1
        tokens_checked = 0
        body_tokens = []

        for token in token_stream:

            tokens_checked += 1

            token_value = token[1]
            token_type  = token[0] 

            if token_type == "SCOPE_DEFINER" and token_value == "{": nesting_count += 1
            elif token_type == "SCOPE_DEFINER" and token_value == "}": nesting_count -= 1

            if nesting_count == 0: 
                body_tokens.append(token)
                break
            else: body_tokens.append(token)

    
        return [body_tokens, tokens_checked]



    def equation_parser(self, equation):
       
        total = 0 # Holds equation value

        for item in range(0, len(equation)):
            
            # Add first value to total as a starting int to perform calculatios on
            if item == 0:
                total += equation[item]
                pass

            # This will check every operator and perform the right calculations based on total
            # and the number that is after the operator
            if item % 2 == 1:
                if equation[item] == "+": total += equation[item + 1]
                elif equation[item] == "-": total += equation[item + 1]
                elif equation[item] == "/": total /= equation[item + 1]
                elif equation[item] == "*": total *= equation[item + 1]
                elif equation[item] == "%": total %= equation[item + 1]
                else: self.send_error_message("Error parsing equation, check that you are using correct operand", equation)

            # Skip every number since we already check and use them
            elif item % 2 == 0: pass
        
        return total



    def concatenation_parser(self, concatenation_list):
    

        full_string = ""

        for item in range(0, len(concatenation_list)):

            current_value = concatenation_list[item]

           if item == 0:
                if current_value[0] == '"':
                    full_string += current_value[1:len(current_value) - 1]
                else:
                    var_value = self.get_variable_value(current_value)
                    if var_value != False:
                        full_string += var_value[1:len(var_value) - 1]
                    else:
                        self.send_error_message('Cannot find variable "%s" because it was never created' % concatenation_list[item + 1], concatenation_list)
                pass
            
            if item % 2 == 1:

                if current_value == "+": 
                    # This checks if the value being checked is a string or a variable
                    if concatenation_list[item + 1][0] != '"': 

                        # This will get the variable value and check if it exists if so then it adds it to the full string
                        var_value = self.get_variable_value(concatenation_list[item + 1])
                        if var_value != False:
                            full_string += var_value[1:len(var_value) - 1]
                        else:
                            self.send_error_message('Cannot find variable "%s" because it was never created' % concatenation_list[item + 1], concatenation_list)

                    else: 
                        full_string += concatenation_list[item + 1][1:len(concatenation_list[item + 1]) - 1]
                        
                elif current_value == ",": 
                    full_string += " " + concatenation_list[item + 1]

                else: 
                    print("Error parsing equation, check that you are using correct operand")
            
            # This will skip value as it is already being added and dealt with when getting the operand
            if item % 2 == 0: pass

        return '"' + full_string + '"'



    def get_variable_value(self, name):
       

        for var in self.symbol_tree:
            if var[0] == name: return var[1]
        return False



    def form_value_list(self, tokens):
        value_list = []
        tokens_checked = 0
        for token in tokens:
            if token[0] == "STATEMENT_END": break
            try: value_list.append(int(token[1]))
            except: value_list.append(token[1])
            tokens_checked += 1

        return [value_list, tokens_checked]



    def send_error_message(self, msg, error_list):
        print("------------------------ ERROR FOUND ----------------------------")
        print(" " + msg)
        print('\033[91m', "".join(str(r) for v in error_list for r in (v[1] + " ") ) , '\033[0m')
        print("-----------------------------------------------------------------")
        quit()