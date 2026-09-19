s = input()
print(sum(c.isupper() for c in s), sum(c.islower() for c in s),
      sum(c.isdigit() for c in s), sum(not c.isalnum() for c in s))
