def parseModule(module):
    mod = {'M': __import__(module)}
    return {name: eval(f'M.{name}', mod) for name in dir(mod['M']) if isinstance(eval(f'M.{name}', mod), type)}
