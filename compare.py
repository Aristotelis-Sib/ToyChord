def compare_query():
    keys_values = []
    counter = 0
    db = {}
    with open('data/insert.txt', 'r') as f:
        for f_line in f:
            line = f_line.rstrip()
            c = line.split(',')
            db[c[0]] = c[1]
            counter += 1

    counter = 0
    with open('data/query.txt', 'r') as f:
        for f_line in f:
            line = f_line.rstrip()
            keys_values.append(db[line])
            counter += 1

    return keys_values


def compare_requests():
    keys_values = []
    counter = 0
    db = {}

    counter = 0
    with open('data/requests.txt', 'r') as f:
        for f_line in f:
            line = f_line.rstrip()
            data = line.split(',')
            keys_values.append(data)
            counter += 1
    result = []
    for data in keys_values:
        if data[0] == 'insert':
            db[data[1]] = data[2]
        else:
            tmp = db.get(data[1])
            if tmp is None:
                result.append("Key not found")
            else:
                result.append(tmp)
    return result
