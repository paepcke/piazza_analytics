
import re
import json

"""This function is used to clean up the HTML tags from all the questions/ answers/ notes/ follow ups/ feedbacks  text etc.
"""
def cleanhtml(self, raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def identify_role(self, task):

    '''Extracting the role of a user based on whether the user_id comes up in a student answer, instructor answer and/ or instructor note
    '''
    user_file = task['input']+'/users.json'
    content_file = task['input'] + '/class_content.json'

    user_data = open(user_file,'r')
    class_data = open(content_file,'r')

    parsed_users = json.load(user_data)
    parsed_class = json.load(class_data)
    types = set()
    instructors = set()
    students = set()

    for record in parsed_class:
        if 'change_log' in record:
            for log in record['change_log']:
                types.add(log['type'])
                if log['type']=='i_answer' or log['type'] == 'i_answer_update':
                    instructors.add(log['uid'])
                if log['type']=='s_answer' or log['type'] == 's_answer_update':
                    students.add(log['uid'])
    return set(instructors), set(students)
