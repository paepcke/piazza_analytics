import re
import json
import csv

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


def get_nodes_and_edges(path):
    weighted_edges = set()
    nodes = set()
    with open(path) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            nodes.add(row[0])
            edge_tuple = (row[0],row[1],int(row[2]))
            if edge_tuple[2]!=0:
                weighted_edges.add(edge_tuple)
    return nodes,weighted_edges

def write_network_to_file(out_file,user_edges):
    fieldnames = ['user1','user2','num_endorsements']
    writer = csv.DictWriter(open(out_file,'w'), fieldnames=fieldnames)
    for key in user_edges:
        writer.writerow({'user1': key[0],'user2': key[1],'num_endorsements':user_edges[key]})
