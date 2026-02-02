# propositional-logic-engine

This project parses propositional logic expressions, validates them,
builds an abstract syntax tree (AST), and generates a full truth table.

## Supported operators
- NOT
- AND
- OR
- -> (implication)

## Example

-Input:
Enter expression: (not not a and (c or b)) -> not d 

-Outputs the following:

       a              b              c              d       a AND c OR b -> NOT d
      True           True           True           True          False           
      True           True           True          False           True           
      True           True          False           True          False           
      True           True          False          False           True           
      True          False           True           True          False           
      True          False           True          False           True           
      True          False          False           True           True           
      True          False          False          False           True
     False           True           True           True           True
     False           True           True          False           True
     False           True          False           True           True
     False           True          False          False           True
     False          False           True           True           True
     False          False           True          False           True
     False          False          False           True           True
     False          False          False          False           True

## Features
- Expression validation
- Tokenization
- AST construction
- Recursive evaluation
- Truth table generation
- Pretty-printed output

## Motivation  
Built as a learning project to deeply understand parsing, recursion,
and logical evaluation.

