import logging

logger_output_file = 'output_logs.log'
logger = logging.getLogger('piazza_application')
logging.basicConfig(filename =logger_output_file, filemode= 'w', level=logging.INFO)

class Config(object):

    """Holds configurable parameters.
       These can be configured by the instructors of the course.
    """
    credit = {}
    credit['questions_asked'] = 1.0
    credit['questions_answered'] = 3.0
    credit['total_posts'] = 1.0
    credit['total_views'] = 0.0
    credit['days_online'] = 0.0
    credit['no_endorsed_answers'] = 5.0
    credit['total_no_endorsements'] = 5.0

    student_endorsement_weight = 1.0
    instructor_endorsement_weight = 1.0

    thresholds = {}
    thresholds['upvotes_on_que'] = 50.0
    thresholds['upvotes_on_i_answer'] = 50.0
    thresholds['upvotes_on_i_answer'] = 50.0
    thresholds['unique_collaborations'] = 50.0
    thresholds['follow_up_thread'] = 50.0
    thresholds['upvotes_on_note'] = 50.0
    thresholds['unique_collaborations_on_note'] = 50.0
    thresholds['follow_up_thread_on_note'] = 50.0




