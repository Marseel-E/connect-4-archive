import typing

def fix(name):
    if name.startswith('<') and name.endswith('>'):
        name = name.replace('<', '')
        name = name.replace('>', '')
    if "circle:" in name:
        name = name.replace('circle:', '')
    if name.startswith(':'):
        name = name.replace(':', '')
    if "_" in name:
        name = name.replace('_', ' ')
    for i in range(10):
        if str(i) in name:
            name = name.replace(str(i), '')
    return name.capitalize()

def unfix(name):
    if " " in name:
        name = name.replace(' ', '_')
    return name

def HL(value):
    return f"`{value}`"

def B(value):
    return f"**{value}**"

def I(value):
    return f"*{value}*"

def CO(value):
    return f"~~{value}~~"

def C(value):
    return f"||{value}||"

def L(value):
    return f"<{value}>"

def U(value):
    return f"__{value}__"

def BOX(value, Type : typing.Optional[str] = False):
    if (Type):
        return f"```{Type}\n{value}\n```"    
    return f"```\n{value}\n```"

def Q(value):
    return f'"{value}"'