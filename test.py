import pickle
import ast

term_dict = {}


postings = {
	"cat" : [1,4,5,(7,5),20,30],
	"dog" : [1,(2,4),3,4,(5,7),6,7,8],
	"watermelon" : [(20,3),30,40,50],
	"zebra" : [(1,4),5,10,40,(50,8),60,70,80,(90,12),100,200,300,(400,16),500,600,700,800,900,1000]
}

f = open('postings.txt','w+')
f2 = open('./dictionary.txt', 'wb')

offset = 0
for k,v in postings.items():
	f.write(str(v) + '\n')
	term_dict[k] = (offset,len(v))
	offset = f.tell()

pickle.dump(term_dict, f2)
f.flush()
f2.flush()



f.close()
f2.close()


f4 = open('postings.txt', 'r')
f3 = open('dictionary.txt', 'rb')

term_dict_test = pickle.load(f3)
f4.seek(term_dict_test["cat"][0])
print(ast.literal_eval(f4.readline().rstrip()))
f4.seek(term_dict_test["dog"][0])
print(ast.literal_eval(f4.readline().rstrip()))
f4.seek(term_dict_test["watermelon"][0])
print(ast.literal_eval(f4.readline().rstrip()))
f4.seek(term_dict_test["zebra"][0])
print(ast.literal_eval(f4.readline().rstrip()))



		    


