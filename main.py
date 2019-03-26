from parser import *


def main():
    while True:
        str_expr = input("> ")
        result: Either = parse(str_expr)
        if result.left:
            print(result)
        else:
            print("<", result.value[0])


if __name__ == '__main__':
    main()
