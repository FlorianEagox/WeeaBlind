import re

test = """
f u c k i e s u w u

"""

pattern = r"\S{7,}"

print(bool(re.search(pattern, test)))