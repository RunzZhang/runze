import sys
sys._excepthook = sys.excepthook
def foo(exctype, value, tb):
    print('My Error Information')
    print('Type:', exctype)
    print('Value:', value)
    print('Traceback:', tb)



def exception_hook(exctype, value, traceback):
    print("ExceptType: ", exctype,"Value: ", value, "Traceback: ", traceback)
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)

sys.excepthook =  exception_hook

def bar(a,b):
    c=a/b
    return c


if __name__=="__main__":
    # sys.excepthook = foo
    # raise RuntimeError("Test unhandlesd")
    print(bar(5,0))