

if __name__ =="__main__":
    point_a = 0
    point_b = 0
    para_a = 3
    para_b = 8
    while point_b<para_b:
        print(point_b)
        try:
            point_b += 1
            if point_a<3:
                point_a += 1
            else:
                raise Exception("A Error")
        except Exception as e:
            print(e)
            continue
    print("END")




