import math


text1 = "Daniel \nTest1 \nTest2 \nTest3 \nTest4 \nTest5 \ntest6"

text2 = "eX+Sk9L7ibVJ+R/s0nPYW5umwXP22TNz6lAkfH9TV7vOznfg7pmvbfQdVFjju+5OVaCkO1i3hmXBOceo6dpnWg=="



def shannon_entropy(data):
    stack = {}
    symbol_list = {}

    for character in data:
        stack[character] = round(data.count(character) / len(data), 5)
        symbol_list[character] = data.count(character)
    # print('\nSymbol-occurrence frequencies:\n')
    # for symbol in stack:
    #     print("{0} --> {1} -- {2}".format(symbol, stack[symbol], symbol_list[symbol]))
    return symbol_frequency(stack)


def symbol_frequency(symbol_set):
    bit_set = [round(symbol_set[symbol] * math.log2(symbol_set[symbol]), 5) for symbol in symbol_set]
    entropy = -1 * (round(sum(bit_set), 5))
    return entropy


print(abs(shannon_entropy(text1)-shannon_entropy(text2)))