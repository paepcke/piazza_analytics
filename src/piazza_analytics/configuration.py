import logging

logger_output_file = '../output_logs.log'
logger = logging.getLogger('piazza_application')
logging.basicConfig(filename =logger_output_file, filemode= 'w', level=logging.INFO)

class Config(object):

    """Holds configurable parameters.
       These can be configured by the instructors of the course.
    """
    credit = {}
    credit['questions_asked'] = 6.0
    credit['questions_answered'] = 8.0
    credit['total_posts'] = 3.0
    credit['total_views'] = 0.5
    credit['days_online'] = 0.5
    credit['no_endorsed_answers'] = 2.0
    credit['total_no_endorsements'] = 3.0
    credit['centrality'] = 10.0
    credit['page_rank'] = 10.0

    student_endorsement_weight = 1.0
    instructor_endorsement_weight = 4.0

    thresholds = {}
    thresholds['upvotes_on_que'] = 50.0
    thresholds['upvotes_on_s_answer'] = 60.0
    thresholds['upvotes_on_i_answer'] = 60.0
    thresholds['unique_collaborations'] = 45.0
    thresholds['follow_up_thread'] = 55.0
    thresholds['upvotes_on_note'] = 50.0
    thresholds['unique_collaborations_on_note'] = 40.0
    thresholds['follow_up_thread_on_note'] = 55.0
    thresholds['unique_views'] = 65.0

    thresholds_for_instructors = {}
    thresholds_for_instructors['upvotes_on_que'] = 65.0
    thresholds_for_instructors['upvotes_on_s_answer'] = 65.0
    thresholds_for_instructors['upvotes_on_i_answer'] = 65.0
    thresholds_for_instructors['unique_collaborations'] = 70.0
    thresholds_for_instructors['follow_up_thread'] = 70.0
    thresholds_for_instructors['upvotes_on_note'] = 40.0
    thresholds_for_instructors['unique_collaborations_on_note'] = 70.0
    thresholds_for_instructors['follow_up_thread_on_note'] = 70.0

    edit_distance_threshold = 15
