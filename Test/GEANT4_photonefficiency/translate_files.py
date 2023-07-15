Pi=3.1415
def wavelength_to_ev(wavelength):
    ev = 1239.8419738620933/wavelength
    return ev

def k_to_abslen(k,wavelength):
    abslen = wavelength/(4*Pi*k)
    return abslen

if __name__=="__main__":
    # f = open("C:\\Users\ZRZ\Desktop\Si.txt","r")
    # f = open("C:\\Users\ZRZ\Desktop\Aspnes.csv", "r")
    # energy=[]
    # wavelength=[]
    # abslen=[]
    # k=[]
    # n=[]
    # start=[]
    # end=[]
    #
    # for x in f:
    #     print("line=",x)
    #     print("2nd char=",x[1])
    #     # for i in range(len(x)):
    #     #     if x[i]==" " and x[i-1]!=" ":
    #     #         end.append[i]


    print(wavelength_to_ev(190))



    # f.close()


