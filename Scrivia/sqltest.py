from cs50 import SQL
import random
import re

# # #de trivdb die ik in deze branch heb gezet staan alle trivia vragen in, deze ook downloaden als je vragen wilt toevoegen
# # db = SQL("sqlite:///trivdb.db")

# # vgq = [] # hier komt een dict die we gelijk in sql kunnen zetten

# # #zet de vragen in sql
# # for x in range(len(vgq)):
# #     vgq_ = vgq[x]
# #     db.execute("INSERT INTO trivia_c (category, difficulty, question, correct, incorrect) VALUES(:category, :difficulty, :question, :correct, :incorrect)",
# #                 category = vgq_["category"], difficulty = vgq_["difficulty"], question = vgq_["question"], correct = vgq_["correct_answer"], incorrect = vgq_["incorrect_answers"])

# # print("DONE")

# # Requesting a question from the api
# def get_questions(category, type):
#     import requests
#     url = 'https://opentdb.com/api.php'
#     if type == 'timeattack':
#         parameters = {'amount': '1', 'type': 'multiple', 'category': category}
#     elif type == 'regular':
#         parameters = {'amount': '1', 'type': 'multiple', 'category': category, 'difficulty': 'easy'}
#     response = requests.get(url, params=parameters)
#     response.raise_for_status()
#     json_response = response.json()['results']
#     return json_response

# def cleanhtml(raw_html):
#     cleanr = re.compile('&.*?;')
#     cleantext = re.sub(cleanr, "'", raw_html)
#     return cleantext

# # Making the question usable in terms of format
# def call_question(cate, type, questionset):
#     question = get_questions(cate, type)[0]
#     intlist =  [int(i) for i in question['correct_answer'].split() if i.isdigit()]
#     if len(intlist) >= 1 or question['correct_answer'] in questionset:
#         return call_question(cate, type, questionset)
#     else:
#         if question["correct_answer"] != 'Cheetah':
#             return call_question(cate, type, questionset)
        
#         answers = question["incorrect_answers"]
#         answers.append(question["correct_answer"])
#         new_answer_0 = cleanhtml(answers[0])
#         new_answer_1 = cleanhtml(answers[1])
#         new_answer_2 = cleanhtml(answers[2])
#         new_answer_3 = cleanhtml(answers[3])
#         new_answers = [new_answer_0, new_answer_1, new_answer_2, new_answer_3]
#         return question["question"], new_answers, question["correct_answer"]


# def getaquestion():

#     questionset = set()
#     catlook = 'animals'

#     category_list = ['animals', 'video_games', 'celebrities', 'comics', 'general_knowledge',
#                         '27', '15', '26', '29', '9']
#     for cat in range(int(len(category_list) / 2.0)):
#         if category_list[cat] == catlook:
#             category = category_list[cat + 5]

#     triv = call_question(category, 'timeattack', questionset)
#     print(triv)
    
#     question = triv[0]
#     all_answers = triv[1]
#     correct = triv[2]

#     random.shuffle(all_answers)

#     questionset.add(correct)

#     return all_answers, question, correct


# getaquestion()





# # cheetah = ['Cheetah', 'Lion', 'Thomson&rsquo;s Gazelle', 'Pronghorn Antelope']
# # for x in cheetah:
# #     newx = remove_html_markup(x)
# #     try:
# #         f = x.index('&')
# #         newx = newx[:f] + "'" + newx[f:]
# #     except:
# #         ValueError

# #     print(newx)
# # print(cheetah)

# # cheetah = ['Cheetah', 'Lion', 'Thomson&rsquo;s Gazelle', 'Pronghorn Antelope']
# # for x in cheetah:
# #     x.strip('&rsquo;')
# #     print(x)


scrivdb = SQL("sqlite:///scrivia.db")

scrivdb.execute("UPDATE timeattack SET comics = comics + :other WHERE username = :username",
                 other=57,
                 username='sava8')
scrivdb.execute("UPDATE timeattack SET points = points + :other WHERE username = :username",
                 other=57,
                 username='sava8')


scrivdb.execute("UPDATE timeattack SET points = points + :other WHERE username = :username",
                 other=30,
                 username='NOAH')








