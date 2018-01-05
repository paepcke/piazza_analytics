import re
import json
import csv
import numpy as np
import scipy.stats as stats
import pylab as pl

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

    # for record in parsed_class:
    #     if 'change_log' in record:
    #         for log in record['change_log']:
    #             types.add(log['type'])
    #             if log['type']=='i_answer' or log['type'] == 'i_answer_update':
    #                 instructors.add(log['uid'])
    #             if log['type']=='s_answer' or log['type'] == 's_answer_update':
    #                 students.add(log['uid'])
    return set(instructors), set(students)


def get_nodes_and_edges(path):
    weighted_edges = set()
    nodes = set()
    with open(path) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            nodes.add(row[0])
            edge_tuple = (row[0],row[1],float(row[2]))
            if edge_tuple[2]!=0:
                weighted_edges.add(edge_tuple)
    return nodes,weighted_edges

def write_nodes_to_file(out_file,user_edges, list_instructors):
    fieldnames = ['user1','user1_role']
    role_dict = {}
    writer = csv.DictWriter(open(out_file,'w'), fieldnames=fieldnames)
    user_set = set()
    for key in user_edges.keys():
        user_set.add(key[0])
        user_set.add(key[1])

    for item in user_set:
        if item in list_instructors:
            role_dict[item] = "instructor"
        else:
            role_dict[item] = "student"

    for k, v in role_dict.items():
        writer.writerow({'user1': k,'user1_role': v})


def write_network_to_file(out_file,user_edges):

    fieldnames = ['Source','Target','Weight']
    writer = csv.DictWriter(open(out_file,'w'), fieldnames=fieldnames)
    for key in user_edges:
        writer.writerow({'Source': key[0],'Target': key[1],'Weight':user_edges[key]})


def get_min_edit_distance(str1, str2, m, n):
    dp = [[0 for x in range(n+1)] for x in range(m+1)]
    for i in range(m+1):
        for j in range(n+1):
            if i == 0:
                dp[i][j] = j
            elif j == 0:
                dp[i][j] = i
            elif str1[i-1] == str2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i][j-1], # Insert
                                   dp[i-1][j], # Remove
                                   dp[i-1][j-1])# Replace

    return dp[m][n]


def plot_data_distribution(h, file_to_save):
    h = sorted(h)
    fit = stats.norm.pdf(h, np.mean(h), np.std(h))
    pl.figure()
    pl.plot(h,fit,'-o')
    pl.hist(h,normed=True)
    pl.savefig(file_to_save)
