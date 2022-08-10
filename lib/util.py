def dump(obj):
    ## Take ANY object, Print all attributes with associated values ##
    for attr in dir(obj):
        print("obj.{a} = {v}".format(a=attr, v=getattr(obj, attr)))

def boolFromStr(str):
    ## Convert a string "true" or "false" into a real boolean value
    if str != None:
        if str.lower() == "true":
            return True
        elif str.lower() == "false":
            return False
        else:
            return None

def legalize( x ):
    # Sanitize string by removing any potentially illegal characters
    ILLEGAL = [
    [" ", "_"],
    [":", ""], [";", ""], ["'", ""],  [",", ""], ["`", ""], ["~", ""], 
    ["/", ""], ["\\", ""], ["\"", ""], ["|", "_"],
    ["(", ""], [")", ""], ["{", ""], ["}", ""], ["[", ""], ["]", ""],
    ["!", ""], ["@", ""], ["#", ""], ["$", ""], ["%", ""], ["^", ""], ["&", ""], ["?", ""], ["*", ""],
    ]
    for i in ILLEGAL:
        x = x.replace(i[0], i[1])
    return x
