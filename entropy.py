import math


text1 = "LONDON — Apparent attacks on two tankers in the Gulf of Oman on Thursday forced their crews to abandon ship and left one vessel ablaze, a month after four tankers were damaged in the same area, raising alarms about the security of a vital passageway for much of the world’s petroleum.\nThe early morning incidents, which two shipping companies involved and the White House described as attacks, elevated tensions in a region already unsettled by the escalating conflict between the United States and some of its allies, and Iran."

text2 = "rKV3ajBbAP5QuJW/qzpkThbtNaLmwQkEC2CtxFAfAoNBfpEKQfnweDIALq/p5poRkpF9ILlW4bVmuH7Elx//H4LbUe0PgYp6seiq58zoi/bLSqB6RKr16gj3isIMa48XJQ0OHbk/k56ziZfvX8RsvqFkTg207bJ3GfFsjhv0XUtc8FuJAryINaCHzsL0svVu3tHJYoFpXpm5BCxnXAZJk/uD+Lnc8SJlErhHUpS8l5zIE70TpedItLPqwcc7zFe13E87NhMaTUWtLIHoy9Wz/c8IHo3Cxu+KpvMmXnu74NFbV2y5LvTsTnC/a74Hc8DmP/qRnWm97bt1JxynTcROLwlHEU/6yXHSITFWYy4RD4Zzkk+6wKuRzzSQN5Furt0qh7CrU4k3Cj8tZbwXJgTSQspHCF7a2IFzs1Wc3Ia4ZEBc2fw42qrYYwR/fQwDsZwhqqvUZQPPR+FVNAMqoPlFAdTWFEhnXB0Al3VmnpsAW3ATlF3PtjtNaa67NxAz9JnAxqJcbiZP3fMQVcq66T+8X+f+ItO+D48p71bA94SAQs1tS1S+xlthYq6PwVDIYo8e2WAjoXeydYAMum9R7rhVxx7F+P+z1qTNoadrTkWy1JWcOxCFkuQuYnRi6sT75AqFtIzik+17ZtSp+bQyoYIl2De4z5o1vI/qoZzGKi0ZEi8w7INNKH6Yiq4lSa8O5+86hfJNoUsfHVN/6Mq2dBjJIw=="



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