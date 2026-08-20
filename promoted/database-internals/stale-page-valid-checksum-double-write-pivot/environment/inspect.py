import importlib.util
_spec=importlib.util.spec_from_file_location("_stdlib_inspect","/usr/local/lib/python3.11/inspect.py")
_module=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
globals().update({name:getattr(_module,name) for name in dir(_module) if not name.startswith("__")})
if __name__=="__main__":
    import json,sys
    print(json.load(open(sys.argv[1])))
