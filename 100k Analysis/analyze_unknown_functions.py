import json
import sqlite3

# connect to database
conn = sqlite3.connect('infer_results.db')

c = conn.cursor()
print("Number of bugs introduced (without TOP) where reason is unknown")

# select all increases where reason is unknown
c.execute("SELECT * FROM Change WHERE INCREASE = TRUE AND REASON IS NULL")
unknown_increases = c.fetchall()
conn.commit()

print("LENGTH:")
print(len(unknown_increases))

polynomial_1_loop_dictionary = {}

polynomial_1_modeled_call_dictionary = {}

loop_model_call_count_at_max_level = {}

max_level_dictionary = {}

found_counter = 0
both_counter = 0
loop_counter = 0
modeled_call_counter = 0
for change in unknown_increases:
    project_id = change[0]
    release_prior = change[1]
    hash = change[2]
    procedure_id = change[3]

    c.execute("SELECT * FROM FUNCTION WHERE project_id = ? AND release_id = ? AND hash = ? AND procedure_id = ?",
              (project_id,
               release_prior,
               hash,
               procedure_id))
    function_prior = c.fetchall()
    if function_prior is None:
        continue

    trace = json.loads(function_prior[0][7])

    # check if trace of function prior is empty (constant function)
    if len(trace) != 0:
        print("Trace length not 0")
        continue
    c.execute("SELECT * FROM FUNCTION WHERE project_id = ? AND release_id = ? AND hash = ? AND procedure_id = ?",
              (project_id, (int(release_prior) + 1), hash, procedure_id))
    function_after = c.fetchone()
    if function_after is None:
        continue
    trace = json.loads(function_after[7])
    max_level = 0
    max_object = None

    # get the maximum level in the trace
    for o in trace:
        if o.get('level') >= max_level:
            max_level = o.get('level')
            max_object = o

    loop_count = 0
    modeled_call_count = 0
    if max_level in max_level_dictionary:
        max_level_dictionary[max_level] += 1
    else:
        max_level_dictionary[max_level] = 1

    # analyze at max_level
    for o in trace:
        if o.get('level') == max_level:
            if o.get('description') == 'Loop':
                if max_level in polynomial_1_loop_dictionary:
                    polynomial_1_loop_dictionary[max_level] += 1
                    found_counter += 1
                else:
                    polynomial_1_loop_dictionary[max_level] = 1
                    found_counter += 1
                loop_count += 1
            if 'Modeled call to' in o.get('description'):
                if max_level in polynomial_1_modeled_call_dictionary:
                    polynomial_1_modeled_call_dictionary[max_level] += 1
                    found_counter += 1
                else:
                    polynomial_1_modeled_call_dictionary[max_level] = 1
                    found_counter += 1
                modeled_call_count += 1

    if loop_count >= 1 and modeled_call_count >= 1:
        both_counter += 1
    elif loop_count >= 1:
        loop_counter += 1
    elif modeled_call_count >= 1:
        modeled_call_counter += 1

sorted(polynomial_1_loop_dictionary)
sorted(polynomial_1_modeled_call_dictionary)
sorted(loop_model_call_count_at_max_level)

# print the amount of loops, modeled_calls, both
print(loop_counter)
print(modeled_call_counter)
print(both_counter)

# print the level of the change
for key, value in max_level_dictionary.items():
    print(f"There are {value} changes at level {key}")

both_counter = 0
loop_counter = 0
modeled_call_counter = 0

print("Number of bugs fixed (without TOP) where reason is unknown")

# select all decreases where reason is unknown
c.execute("SELECT * FROM Change WHERE INCREASE = FALSE AND REASON IS NULL")
unknown_increases = c.fetchall()
conn.commit()

print("LENGTH:")
print(len(unknown_increases))

polynomial_1_loop_dictionary = {}

polynomial_1_modeled_call_dictionary = {}

loop_model_call_count_at_max_level = {}

max_level_dictionary = {}

found_counter = 0
both_counter = 0
loop_counter = 0
modeled_call_counter = 0
for change in unknown_increases:
    project_id = change[0]
    release_prior = change[1]
    hash = change[2]
    procedure_id = change[3]

    c.execute("SELECT * FROM FUNCTION WHERE project_id = ? AND release_id = ? AND hash = ? AND procedure_id = ?",
              (project_id, (int(release_prior) + 1), hash, procedure_id))
    function_after = c.fetchall()

    if function_after is None:
        continue

    trace = json.loads(function_after[0][7])
    # check if trace of function after is empty (constant function)
    if len(trace) != 0:
        continue
    c.execute("SELECT * FROM FUNCTION WHERE project_id = ? AND release_id = ? AND hash = ? AND procedure_id = ?",
              (project_id,
               release_prior,
               hash,
               procedure_id))
    function_prior = c.fetchone()

    if function_prior is None:
        continue
    trace = json.loads(function_prior[7])
    max_level = 0
    max_object = None

    # get the maximum level in the trace
    for o in trace:
        if o.get('level') >= max_level:
            max_level = o.get('level')
            max_object = o

    if max_level in max_level_dictionary:
        max_level_dictionary[max_level] += 1
    else:
        max_level_dictionary[max_level] = 1
    loop_count = 0
    modeled_call_count = 0

    # analyze at max_level
    for o in trace:
        if o.get('level') == max_level:
            if o.get('description') == 'Loop':
                if max_level in polynomial_1_loop_dictionary:
                    polynomial_1_loop_dictionary[max_level] += 1
                    found_counter += 1
                else:
                    polynomial_1_loop_dictionary[max_level] = 1
                    found_counter += 1
                loop_count += 1
            if 'Modeled call to' in o.get('description'):
                if max_level in polynomial_1_modeled_call_dictionary:
                    polynomial_1_modeled_call_dictionary[max_level] += 1
                    found_counter += 1
                else:
                    polynomial_1_modeled_call_dictionary[max_level] = 1
                    found_counter += 1
                modeled_call_count += 1

    if loop_count >= 1 and modeled_call_count >= 1:
        both_counter += 1
    elif loop_count >= 1:
        loop_counter += 1
    elif modeled_call_count >= 1:
        modeled_call_counter += 1

for key, value in max_level_dictionary.items():
    print(f"There are {value} changes at level {key}")

sorted(polynomial_1_loop_dictionary)
sorted(polynomial_1_modeled_call_dictionary)
sorted(loop_model_call_count_at_max_level)

print(loop_counter)
print(modeled_call_counter)
print(both_counter)
