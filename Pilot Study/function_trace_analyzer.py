import json
import sqlite3

# connect to database
conn = sqlite3.connect('database/infer_results.db')

c = conn.cursor()
c.execute("SELECT * FROM FUNCTION WHERE polynomial = 1 GROUP BY procedure_id")

polynomial_1_results = c.fetchall()

print("LENGTH:")
print(len(polynomial_1_results))


polynomial_1_loop_dictionary = {}

polynomial_1_modeled_call_dictionary = {}

loop_model_call_count_at_max_level = {}

found_counter = 0
for function in polynomial_1_results:
    trace = json.loads(function[7])

    max_level = 0
    max_object = None
    for o in trace:
        if o.get('level') >= max_level:
            max_level = o.get('level')
            max_object = o

    loop_count = 0
    modeled_call_count = 0
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
    if loop_count > 1 or modeled_call_count > 1 or (loop_count + modeled_call_count) > 1:
        key = (loop_count, modeled_call_count)
        if modeled_call_count == 10:
            print(function)
        if key in loop_model_call_count_at_max_level:
            loop_model_call_count_at_max_level[key] += 1
        else:
            loop_model_call_count_at_max_level[key] = 1

sorted(polynomial_1_loop_dictionary)
sorted(polynomial_1_modeled_call_dictionary)
sorted(loop_model_call_count_at_max_level)

for key, value in polynomial_1_loop_dictionary.items():
    print(f"There are {value} loops at level {key}")

for key, value in polynomial_1_modeled_call_dictionary.items():
    print(f"There are {value} modeled_calls at level {key}")

for key, value in loop_model_call_count_at_max_level.items():
    print(f"There are {value} functions with {key[0]} loop calls and {key[1]} modeled calls at max_level")

c.execute("SELECT COUNT(*) FROM FUNCTION")
conn.commit()
print(c.fetchone())

c.execute("SELECT COUNT(*) FROM FUNCTION WHERE polynomial = 1")
conn.commit()
print(c.fetchone())

print(found_counter)
