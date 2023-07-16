import pandas as pd
from . import use_api
import openai
from tika import parser
import sys,os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))


def get_job(): # csv파일에 있는 직업 skill을 list화
    path = './csv/job.csv'
    df = pd.read_csv(path)
    df.fillna('', inplace=True)
    jobs = df.values.tolist()
    result = list()
    for job in jobs:
        skills = job[4]
        skills = skills.replace("/", ",")
        if skills == "":
            continue
        skills = use_api.getToken(skills.lower(), tk=',')
        skills = [tok.strip() for tok in skills]
        tmp = {
            "occupation3Nm" : job[2],
            "skill" : skills
        }
        result.append(tmp)
    return result

def jaccard_distance(user_skills, job_skills): #자카드 유사도
    s1 = set(user_skills)
    s2 = set(job_skills)
    intersection = 0 # 교집합 
    for job_skill in job_skills: #문자열 전처리가 완벽히 되지 않아 find로 찾기 ex) 'java -8' , 'java'와는 같은 skill로 처리
        for user_skill in user_skills:
            if user_skill.find(job_skill) != -1:
                intersection = intersection + 1
                break
    return float(intersection / len(s2.union(s1)))


def getUserSkill_to_GPT_Chat(resume): # 이력서의 skill을 GPT를 활용하여 추출
    API_KEY = "USE_KEY"
    openai.api_key= API_KEY
    MODEL = "gpt-3.5-turbo"

    question = "\n Please extract skill, graduation department, and certificate from the corresponding sentence. I don't need another sentence, but please answer in Korean. For example, do it like 'java/C++/OOP'." #prompt
    response = openai.ChatCompletion.create(
        model = MODEL,
        messages = [
            {"role" : "user", "content" : resume+question}, #request
            {"role" : "assistant", "content" : "Help me extract skill from my resume.The response format divides each skill into."}
        ],
        temperature=0
    )
    return response.choices[0].message.content


def recommend_job(pdf): # 직업 추천
    try:
        resume = pdf_to_text(pdf) # 이력서 pdf -> text(string)
        jobs = get_job() # csv파일의 job list
        user_skill = getUserSkill_to_GPT_Chat(resume) 
        user_skill = user_skill.replace('/', ',')
        user_skill = use_api.getToken(user_skill.lower(), ",")
        user_skill = [tok.strip() for tok in user_skill]
        result = list()
        for job in jobs:
            distance = jaccard_distance(user_skill, job['skill'])
            tmp = [job, distance]
            if distance > 0:
                result.append(tmp)
        result.sort(key=lambda x:x[1], reverse=True) # 자카드 distance기준으로 내림차순 정렬
        return result[0]
    except Exception as e:
        print(e)
        


def pdf_to_text(pdf): # pdf -> text 
    resume = parser.from_file(pdf)
    resume = resume['content'].strip()
    return resume
    

