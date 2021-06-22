from contextlib import redirect_stdout

#converts date(2020/06/15) to seperate int variables
def date_to_int(date):
    year, month, date = list(map(int, date.split('/')))

    return year, month, date

#create a subset of all cases after a given date
def get_subset(all_cases, date):
    subset = []
    y1, m1, d1 = date_to_int(date)

    for case in reversed(all_cases):
        y2, m2, d2 = date_to_int(case['個案研判日'])
        if y2 > y1:
            subset.append(case)
        elif y2 == y1 and m2 > m1:
            subset.append(case)
        elif y2 == y1 and m2 == m1 and d2 >= d1:
            subset.append(case)
        else:
            break

    return subset
    
#gives an option to write the results to a txt file
def write_to_txt(fun, input_date, *args):
    ans = input('是否將數據輸出成.txt檔? (Y/N): ')
    if ans == 'Y' or ans == 'y':
        file_name = input('輸入檔名: ') + '.txt' 
        with open(file_name, 'w') as f:
            with redirect_stdout(f):
                print('輸入日期: ', input_date)
                fun(*args)