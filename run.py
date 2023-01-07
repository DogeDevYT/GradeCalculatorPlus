from selenium import webdriver
from selenium.webdriver.common.by import By
from collections import defaultdict
from statistics import mean
import time

summative_weighting_factor = 0.75
formative_weighting_factor = 0.25

# main entering grades loop function
def grade_loop(grade_list):
    while True:
        grade = input('Enter a number grade (no fractions or percentages!) (Type \'stop\' to stop the loop)')
        if grade != 'stop':
            grade_list.append(grade)
        else:
            break
    grade_list = [int(numeric_string) for numeric_string in grade_list]  # convert into integer list
    return grade_list


# function to calculate preEOC Average (also works for non EOC courses since EOC score is averaged with pre eoc average)
def average(summatives, formatives):
    #https://www.wikihow.com/Calculate-Weighted-Average
    return (mean(summatives) * summative_weighting_factor) + (
                mean(formatives) * formative_weighting_factor)


# function to calculate the lowest grade possible and still get the desired score
def lowest_grade(desiredGrade, summatives, formatives):
    current_grade = average(summatives, formatives)
    #(current_grade + x)/2 = desiredGrade
    #current grade + x = 2(desiredGrade)
    # x = 2(desiredGrade) - current grade
    missing_grade = (2 * desiredGrade) - current_grade
    missing_grade_summative = missing_grade * summative_weighting_factor
    missing_grade_formative = missing_grade * formative_weighting_factor
    result = [missing_grade_summative, missing_grade_formative]
    return result


# abstracts the pre EOC grade calculating process to make it easier for me to code
def calculate_grade_final(summatives, formatives, course):
    print('Please enter your FORMATIVE grades:')
    formatives = grade_loop(formatives)
    #formatives = [int(numeric_string) for numeric_string in formatives] #convert into integer list
    print('FORMATIVES for ' + str(course) + ':' + str(formatives))
    print('Please enter your SUMMATIVE grades:')
    summatives = grade_loop(summatives)
    #summatives = [int(numeric_string) for numeric_string in summatives] #convert into integer list
    print('SUMMATIVES for ' + str(course) + ':' + str(summatives))
    # https://www.wikihow.com/Calculate-Weighted-Average
    average_grade = average(summatives, formatives)
    print('Average for ' + str(course) + ':' + str(average_grade))
    desired_end_grade = int(input('What is your desired end grade for ' + str(course) + '? '))
    #TODO: implement logic for determining the lowest grade I can get and still have a desired_end_grade also remember to change desired end grade to actually be right (reasonable answer come on)
    lowest_grade_possible = lowest_grade(desired_end_grade, summatives, formatives)

# Create a webdriver object (basically the browser to use)
driver = webdriver.Chrome()

# Navigate to the webpage containing the button
driver.get('https://campus.forsyth.k12.ga.us/campus/portal/students/forsyth.jsp')

# Locate the button by its ID and click on it to start SSO process
driver.find_element_by_id('samlLoginLink').click()

# wait so that user can input their login data
time.sleep(10)

# find login button and login
driver.find_element_by_id('submitButton').click()

# wait for load
time.sleep(5)

# navigate to grades page
driver.find_element_by_id('menu-toggle-button').click()
time.sleep(1)
driver.find_element_by_partial_link_text('Grades').click()

# parse through courses.txt and input the courses and their ids into a dictionary(<course name>, <course id in
# Infinite Campus>)
courses = defaultdict(list)
with open("courses.txt") as courses_file:
    for line in courses_file:
        course_name, course_id = line.split(":", 1)
        courses[course_name] = course_id.strip()  # gotta remove the newline character (\n)

# parse through query.txt to get other necessary parameters for the end URL query
funky_url_parameters = ''
with open("query.txt") as query_file:
    for line in query_file:
        funky_url_parameters += line
        funky_url_parameters += "&"

################################
#           TESTING            #
#                              #
#            ZONE              #
#                              #
################################

# make final query
#final_query = 'https://campus.forsyth.k12.ga.us/campus/nav-wrapper/student/portal/student/classroom/grades/student-grades?' + funky_url_parameters + "classroomSectionID=" + str(courses["AP American Lit Lang/Comp"])
# open course in selenium
#driver.get(final_query)

def course_loop():
    while True:
        print(courses.keys())
        next_course = input('What course would you like to calculate next? (Type \'stop\' to stop)')
        if next_course == 'stop':
            break
        else:
            pass

course_loop()
