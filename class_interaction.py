#class can call each other and form a loop but this won't kill the code
class One():
    def __init__(self):
        self.one=1
        self.two=Two(self)
        print("loop",self.two.class2.two.class2.two.class2.one)


class Two():
    def __init__(self,someclass):
        self.class2 = someclass
        print("single output", self.class2.one)

# this class including two functions form a loop can kill the code
class Three():
    def __init__(self):
        self.three=3

    def fake_one(self,number=2):
        self.three=self.fake_two()+number

    def fake_two(self,number=2):
        self.three=self.fake_one()+number


if __name__=="__main__":
    one=One()
    three=Three()
    three.fake_one()
    print(three.three)
