import errno
import string
d = dict.fromkeys(string.ascii_lowercase, 0)

#name = input("What is the files name?\n")
name = 'sample'
try:
    s = open(name+'.txt', "rt")
    # actual processing goes here
    for t in s.read():
        t = t.lower()
        if t in d:
            d[t] += 1
    s.close()

except Exception as exc:
    if exc.errno == errno.ENOENT:
        print("The file doesn't exist.")
    elif exc.errno == errno.EMFILE:
        print("You've opened too many files.")
    else:
        print("The error number is:", exc.errno)

list = d.items()
list = sorted(list,key= lambda letter: letter[1], reverse= True)
index = 0
while index < len(list):
    if list[index][1]== 0:
        del list[index]
    else:
        index += 1

hist = open(name+'hist.txt', "wt")
for iter in list:
    hist.writelines(iter[0]+" -> "+str(iter[1])+'\n')
hist.close()
