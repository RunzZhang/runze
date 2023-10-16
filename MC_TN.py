import numpy as np
def check_exp_relation():
    E=[125,250,500,1000]
    lamda = [2.63, 3.53, 5.32, 7.29]
    t=[335, 362, 413, 438]
    ratio =[]
    for i in range(4):
        number = lamda[i]/(t[i]*np.sqrt(E[i]))
        # number = lamda[i] / (t[i])
        print(number)
        ratio.append(number)
    print(number)

class Fst_MC_class():
    def __init__(self):
        E1_list =[]
        E2_list =[]
        E3_list =[]


if __name__=="__main__":
    check_exp_relation()
    print(2, np.sqrt(4))