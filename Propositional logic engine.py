import re
from itertools import product

binary_keywords = ["AND", "OR", "->"]
unary_keywords = ["NOT"]
keywords = binary_keywords + unary_keywords

def is_valid(expr: str) -> bool:
    format_check = expr
    parenthesis_stack = []
    valid_characters = set("abcdefghijklmnopqrstuvwxyz()" + " ")
    #Checks for correct format on binary_keywords, and if it's correct it turns the binary_keywords into 0's
    #That's so that future checks don't see binary_keywords as letters 
    for kw in binary_keywords:
        if kw.upper() in format_check.upper(): # upper to ignore case
            keyword_pattern = rf"[a-z()]+\s+{re.escape(kw)}\s+[a-z()]+"
            if re.search(keyword_pattern, format_check, flags=re.IGNORECASE):
                format_check = re.sub(kw, "0", format_check, flags=re.IGNORECASE)
            else:        
                
                return False
            
    #Unary keywords are 1's        
    for kw in unary_keywords:
        if kw.upper() in format_check.upper(): # upper to ignore case
            keyword_pattern = rf"{re.escape(kw)}\s+[a-z]+|{re.escape(kw)}\s*[()]+"
            if re.search(keyword_pattern, format_check, flags=re.IGNORECASE):
                format_check = re.sub(kw, "1", format_check, flags=re.IGNORECASE)
            else:        
                
                return False
    
    #No unary keyword right next to anything
    if re.search("[a-z01]1|1[a-z01]|11", format_check):
        return False
    
    #Checks for no two non-keyword letter sequence even with blank spaces in between
    format_check = format_check.replace(" ", "")
    
    if re.search(r"[a-z]{2,}", format_check):       
        return False

    #Checks for no parentheses next to binary_keywords
    if re.search(r"\(0", format_check):
        return False

    if re.search(r"0\)", format_check):
        return False


    #Checks parenthesis format is correct   
    for ch in format_check: 
        if ch == "(":
            parenthesis_stack.append("()")
        elif ch == ")":
            if parenthesis_stack:   
                parenthesis_stack.pop()     
            else:
                return False #invalidates immediately because of no "(" before ")"

    if parenthesis_stack:
        return False


    format_check = format_check.replace("0", "")
    format_check = format_check.replace("1", "")
    if (set(format_check) <= valid_characters) == False:
        return False
    
    return True


def tokenize(expr):
    tokens = []
    i = 0

    while i < len(expr):
        matched = False

        if expr[i].isspace():
            i += 1
            continue
        for kw in keywords:
            if expr[i:i+len(kw)].upper() == kw:
                tokens.append(kw.upper())
                i += len(kw)
                matched = True
                break
        if matched:
            continue
        tokens.append(expr[i])
        i += 1
    return tokens

def ast_to_string(node): #Recursively unwraps a node into printable shape and prints it
    if isinstance(node, str):
        return node

    if len(node) == 1:
        return ast_to_string(node[0])
    
    if len(node) == 2:
        op, right = node
        return f"{op} {ast_to_string(right)}"


    if len(node) == 3:
        left, op, right = node
        return f"({ast_to_string(left)} {op} {ast_to_string(right)})"

    raise ValueError("Invalid AST node")


def build_ast(tokenized_expression):
    ast_stack = []


    def try_collapse_not():
        while (
            len(ast_stack) >= 2  
            and isinstance(ast_stack[-2], str)
            and ast_stack[-2] == "NOT"
            and ast_stack [-1] != "("         
        ):
            expr = ast_stack.pop()
            op = ast_stack.pop()
            if isinstance(expr, tuple) and expr[0] == "NOT":               
                ast_stack.append(expr[1])

            elif expr == "NOT":
                return
            else:
                node = (op, expr)                
                ast_stack.append(node) 
        return
        

    for token in tokenized_expression: #pushes, reaches ")", then stops and pops instead, then repeats the process.       
        if token == ")":
            chunk = []

            while True: #pops contents and converts it into a node
                last = ast_stack.pop()
                if last == "(":
                    break
                chunk.append(last)
            chunk.reverse()
            node = tuple(chunk)
            if len(chunk) == 1:
                node = chunk[0]
            else:
                node = tuple(chunk)

            ast_stack.append(node)
            try_collapse_not()
            continue      
        ast_stack.append(token)
        
        try_collapse_not()
   


    if len(ast_stack) == 0:
        raise ValueError("Empty expression")

    if len(ast_stack) != 1:
        ast_stack = tuple(ast_stack)
    else:
        return tokenized_expression[0]
    
    
    
    return ast_stack 

def get_variables(tokenized_expression) -> set[str]:
    allowed_variables = "abcdefghijklmnopqrstuvwxyz"
    variables = {
        token for token in tokenized_expression if token in allowed_variables
    }
    return sorted(variables)


def build_truth_table(variables, expr):  #expr is ast output
    truth_table = []

    def gen_env(vars): 
        for value in product([True, False], repeat = len(vars)):
            env = dict(zip(vars, value))
            yield env

        

    
    def evaluate(expr, env):
        if not isinstance(expr, tuple):
            return env[expr]
        
        if len(expr) == 1:
            return evaluate(expr[0], env)
        
        if len(expr) == 2: #lenght is 2 so we asume expr[0] is "NOT". For more keywords impementation add match with each keyword
            return not evaluate(expr[1], env)
        
        if len(expr) == 3: #middle one will always be a keyword
            match expr[1]:
                case "AND":
                    return evaluate(expr[0], env) and evaluate(expr[2], env)
                case "OR":
                    return evaluate(expr[0], env) or evaluate(expr[2], env)
                case "->":
                    return (not (evaluate(expr[0], env)) or evaluate(expr[2], env))
                    
    for env in gen_env(variables):
        result = evaluate(expr, env) 
        truth_table.append([env, result])
    return truth_table

def print_truth_table(table, variables, printable_expr):
    col_width = 15
    header = "".join(var.center(col_width) for var in variables)
    header += f"{printable_expr}".center(col_width) 
    print(header)

    for env, result in table:
        row = "".join(f"{env[var]}".center(col_width) for var in variables)
        row +=  f"{result}".center(col_width)
        print(row)

def reject_high_variable_count(variables, max_count):
    if len(variables) > max_count:
        raise ValueError(f"The amount of variables is too high, please enter an expression with {max_count} or less variables")




def main():
    max_variable_count = 5

    while True:
        user_input = input("Enter expression: ")
        tokenized_expression = tokenize(user_input)
        variables = get_variables(tokenized_expression)

        

        if not is_valid(user_input):
            print("Invalid expression, please try again")
            continue

        try:
            reject_high_variable_count(variables, max_variable_count)
            ast = build_ast(tokenized_expression)
            printable_expr = ast_to_string(ast)
            truth_table = build_truth_table(variables, ast)
            print_truth_table(truth_table, variables, printable_expr)
            break
        except ValueError as e:
            print(e)

            
main()





