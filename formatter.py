def plurals(n, form1, form2, form3):
    if n == 0:
        return f'{n} {form3}'
    n = abs(n) % 100
    if n > 10 and n < 20:
        return f'{n} {form3}'
    n %= 10
    if n > 1 and n < 5:
        return f'{n} {form2}'
    if n == 1:
        return f'{n} {form1}'
    return f'{n} {form3}'
