import re
# utility to parse mysql reserved keyword list from 'mysql_reserved_keywords'
with open('mysql_reserved_keywords.txt') as f:
    data = f.read()
    pattern = re.compile(r'\( \'([a-zA-Z]+)\', .+? \),')
    result = re.findall(pattern, data)
    print(result)
