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