from cs50 import SQL
import random
import re

# #de trivdb die ik in deze branch heb gezet staan alle trivia vragen in, deze ook downloaden als je vragen wilt toevoegen
# db = SQL("sqlite:///trivdb.db")

# vgq = [] # hier komt een dict die we gelijk in sql kunnen zetten

# #zet de vragen in sql
# for x in range(len(vgq)):
#     vgq_ = vgq[x]
#     db.execute("INSERT INTO trivia_c (category, difficulty, question, correct, incorrect) VALUES(:category, :difficulty, :question, :correct, :incorrect)",
#                 category = vgq_["category"], difficulty = vgq_["difficulty"], question = vgq_["question"], correct = vgq_["correct_answer"], incorrect = vgq_["incorrect_answers"])

# print("DONE")

# Requesting a question from the api
def get_questions(category, type):
    import requests
    url = 'https://opentdb.com/api.php'
    if type == 'timeattack':
        parameters = {'amount': '1', 'type': 'multiple', 'category': category}
    elif type == 'regular':
        parameters = {'amount': '1', 'type': 'multiple', 'category': category, 'difficulty': 'easy'}
    response = requests.get(url, params=parameters)
    response.raise_for_status()
    json_response = response.json()['results']
    return json_response
    
# Making the question usable in terms of format
def call_question(cate, type, questionset):
    question = get_questions(cate, type)[0]
    intlist =  [int(i) for i in question['correct_answer'].split() if i.isdigit()]
    if len(intlist) >= 1 or question['correct_answer'] in questionset:
        return call_question(cate, type, questionset)
    else:
        if question["correct_answer"] != 'Cheetah':
            return call_question(cate, type, questionset)
        return question


def cleanhtml(raw_html):
    cleanr = re.compile('&.*?;')
    cleantext = re.sub(cleanr, "'", raw_html)
    return cleantext



def getaquestion():
    questionset = set()
    catlook = 'animals'

    category_list = ['animals', 'video_games', 'celebrities', 'comics', 'general_knowledge',
                        '27', '15', '26', '29', '9']
    for cat in range(int(len(category_list) / 2.0)):
        if category_list[cat] == catlook:
            category = category_list[cat + 5]

    triv = call_question(category, 'timeattack', questionset)

    correct = triv['correct_answer']
    question = triv["question"]
    answers = triv["incorrect_answers"]
    answers.append(correct)

    # print(answers)
    
    new_answer_0 = cleanhtml(answers[0])
    new_answer_1 = cleanhtml(answers[1])
    new_answer_2 = cleanhtml(answers[2])
    new_answer_3 = cleanhtml(answers[3])
    new_answers = [new_answer_0, new_answer_1, new_answer_2, new_answer_3]
    print(new_answers)
    # new_answer = remove_html_markup(answers[1])
    # try:
    #     en = answers[1].index('&')
    #     new_answer = new_answer[:en] + "'" + new_answer[en:]
    # except:
    #     ValueError

    random.shuffle(answers)
    questionset.add(correct)
    return new_answers, question


getaquestion()





# cheetah = ['Cheetah', 'Lion', 'Thomson&rsquo;s Gazelle', 'Pronghorn Antelope']
# for x in cheetah:
#     newx = remove_html_markup(x)
#     try:
#         f = x.index('&')
#         newx = newx[:f] + "'" + newx[f:]
#     except:
#         ValueError

#     print(newx)
# print(cheetah)

# cheetah = ['Cheetah', 'Lion', 'Thomson&rsquo;s Gazelle', 'Pronghorn Antelope']
# for x in cheetah:
#     x.strip('&rsquo;')
#     print(x)
    
    
    



