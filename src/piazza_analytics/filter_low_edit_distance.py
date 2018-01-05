import json
from utils import *
from configuration import *

def get_minimal_update_pairs(task):
    config_inst = Config()
    user_file = task['input']+'/users.json'
    content_file = task['input'] + '/class_content.json'

    user_data = open(user_file,'r')
    class_data = open(content_file,'r')

    parsed_users = json.load(user_data)
    parsed_class = json.load(class_data)

    low_edit_uids = {}
    # for record in parsed_class:
    #     if 'change_log' in record:
    #         s_answer = False
    #         s_answer_update = False
    #         for log in record['change_log']:
    #             if log['type']=='s_answer':
    #                 creating_uid = log['uid']
    #                 s_answer = True
    #             if log['type'] == 's_answer_update':
    #                 updating_uid = log['uid']
    #                 s_answer_update = True

    #         if s_answer and s_answer_update and creating_uid != updating_uid:
    #             if 'children' in record:
    #                 for item in record['children']:
    #                     if 'history' in item:
    #                         for hist_item in item['history']:
    #                             if hist_item['uid'] == creating_uid:
    #                                 original = hist_item['content']
    #                             elif hist_item['uid'] == updating_uid:
    #                                 updated = hist_item['content']


    #                         edit_dist = get_min_edit_distance(original, updated, len(original), len(updated))
    #                         if edit_dist < config_inst.edit_distance_threshold:
    #                             if updating_uid not in low_edit_uids:
    #                                 low_edit_uids[updating_uid] = []
    #                             low_edit_uids[updating_uid].append(edit_dist)
    return low_edit_uids
