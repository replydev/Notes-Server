def readFile(filename):
    f = open(filename,'r')
    s = f.read()
    f.close()
    return s