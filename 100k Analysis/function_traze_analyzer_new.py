import json
import sqlite3

# connect to database
conn = sqlite3.connect('infer_results.db')

c = conn.cursor()
# select all functions with non-constant polynomial
c.execute("SELECT * FROM FUNCTION WHERE polynomial >= 1  and polynomial <= 20 GROUP BY procedure_id")

polynomial_1_results = c.fetchall()

print("LENGTH:")
print(len(polynomial_1_results))

# dictionaries to store results
loop_dictionary = {}
modeled_call_dictionary = {}
loop_model_call = {}

found_counter = 0
# iterate through functions
for function in polynomial_1_results:
    trace = json.loads(function[7])

    max_level = 0
    max_object = None
    # get maximum level from trace
    for o in trace:
        if o.get('level') >= max_level:
            max_level = o.get('level')
            max_object = o

    loop_count = 0
    modeled_call_count = 0
    loop = False
    modeled_call = False
    # iterathe through trace
    for o in trace:
        if o.get('level') == max_level:
            if o.get('description') == 'Loop':
                loop = True
            if 'Modeled call to' in o.get('description'):
                modeled_call = True
    if loop and modeled_call:
        if max_level in loop_model_call:
            loop_model_call[max_level] += 1
            found_counter += 1
        else:
            loop_model_call[max_level] = 1
            found_counter += 1
    elif loop:
        if max_level in loop_dictionary:
            loop_dictionary[max_level] += 1
            found_counter += 1
        else:
            loop_dictionary[max_level] = 1
            found_counter += 1
    elif modeled_call:
        if max_level in modeled_call_dictionary:
            modeled_call_dictionary[max_level] += 1
            found_counter += 1
        else:
            modeled_call_dictionary[max_level] = 1
            found_counter += 1

for key, value in loop_dictionary.items():
    print(f"There are {value} loops at level {key}")

for key, value in modeled_call_dictionary.items():
    print(f"There are {value} modeled_calls at level {key}")

for key, value in loop_model_call.items():
    print(f"There are {value} functions with {key} both at max_level")

print(found_counter)
