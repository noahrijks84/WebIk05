from cs50 import SQL
import random

#de trivdb die ik in deze branch heb gezet staan alle trivia vragen in, deze ook downloaden als je vragen wilt toevoegen
db = SQL("sqlite:///trivdb.db")

vgq = #hier komt een dict die we gelijk in sql kunnen zetten

#zet de vragen in sql
for x in range(len(vgq)):
    vgq_ = vgq[x]
    db.execute("INSERT INTO trivia_c (category, difficulty, question, correct, incorrect) VALUES(:category, :difficulty, :question, :correct, :incorrect)",
                category = vgq_["category"], difficulty = vgq_["difficulty"], question = vgq_["question"], correct = vgq_["correct_answer"], incorrect = vgq_["incorrect_answers"])

print("DONE")



# VGlist = db.execute("SELECT correct FROM trivia_a")
# print(VGlist)

###################################



#deze code selecteert 4 random vragen en zet deze in variabelen die we makkelijk kunnen gebruiken in html (mbv jinja)
triv = db.execute("SELECT question, correct, incorrect FROM trivia_a ORDER BY RANDOM() LIMIT 4")
print(triv[0])
correct0 = triv[0]['correct']
correct1 = triv[1]['correct']
correct2 = triv[2]['correct']
correct3 = triv[3]['correct']
question0 = triv[0]["question"]
question1 = triv[1]["question"]
question2 = triv[2]["question"]
question3 = triv[3]["question"]
inc0 = triv[0]["incorrect"]
inc1 = triv[1]["incorrect"]
inc2 = triv[2]["incorrect"]
inc3 = triv[3]["incorrect"]

answers0 = inc0.split("'")
answers0.append(correct0)
random.shuffle(answers0)

answers1 = inc1.split("'")
answers1.append(correct1)
random.shuffle(answers1)

answers2 = inc2.split("'")
answers2.append(correct2)
random.shuffle(answers2)

answers3 = inc3.split("'")
answers3.append(correct3)
random.shuffle(answers3)