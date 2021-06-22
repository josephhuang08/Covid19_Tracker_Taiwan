import requests
import util
from datetime import datetime, timedelta

'''
data from 政府資料開放平台 衛生福利部疾病管制署
https://data.gov.tw/dataset/120711

Json query example:
{
    "確定病名": "嚴重特殊傳染性肺炎",
    "個案研判日": "2020/01/22", 
    "縣市": "空值", 
    "鄉鎮": "空值", 
    "性別": "女", 
    "是否為境外移入": "是", 
    "年齡層": "55-59", 
    "確定病例數": "1"
}
'''
#sort reported case numbers by cities and districrts 
def sort_by_location(case_list):
    #city_district is a nested dictionary
    # {'縣市1': { '總共': '確診病例數', '鄉鎮1': '確診病例數', '鄉鎮2': '確診病例數', ... }
    #  '縣市2': { '總共': '確診病例數', '鄉鎮1': '確診病例數', '鄉鎮2': '確診病例數', ... }...}
    city_district = {}

    for case in case_list:
        #store info of '縣市', 鄉鎮 and '確定病例數' in variables
        city = case.get('縣市')
        district = case.get('鄉鎮')
        case_num = int(case.get('確定病例數'))

        #create dictionary of citys and sub dictionary of districts 
        if city not in city_district:
            city_district.update({city: {'總共': 0}})
        if district not in city_district[city]:
            city_district[city].update({district: 0})

        #increment the case counter
        city_district[city]['總共'] += case_num
        city_district[city][district] += case_num

    return city_district       

def print_by_location(city_district):
    for key, value in city_district.items():
        print('{}   總確診: {}人'.format(key, value['總共']))
        print('----------------------')
        count = 0 # Print a new line for every 5 disticts
        for count, district in enumerate(city_district[key].keys(), start = -1): # -1 is '總共'
            if district != '總共':
                if count % 5 == 0 and count != 0:
                    print('\n')
                    count = 0
                print('{}: {:>4}\t'.format(district, city_district[key][district]), end = '')
        if key == '空值':
            print('\n*空值為本土疫情爆發前境外移入病例多於機場或\n集中檢疫所採檢確診並即隔離治療，故未標示其縣市資訊。\naka官方沒給資料', end = '')
        print('\n\n')     
 
def sort_by_gender(case_list):
    gender_count = {'男': 0, '女': 0}

    for case in case_list:
        gender = case.get('性別')
        case_num = int(case.get('確定病例數'))

        if gender == '男':
            gender_count['男'] += case_num
        if gender == '女':
            gender_count['女'] += case_num
    
    return gender_count

def print_by_gender(gender_count):
    total_cases = gender_count['男'] + gender_count['女']
    print('總確診: {}人\n分別為  男性: {}人\t女性: {}人'.format(
        total_cases, gender_count['男'], gender_count['女']))

#sort reported cases by age groups
def sort_by_age(case_list):
    age_groups = {}

    for case in case_list:
        case_num = int(case.get('確定病例數'))
        group = case.get('年齡層')

        #check for the 3 types of age group and store as int for later on sorting
        if len(group) == 1: #group 1: for age groups 0, 1, 2, 3, 4
            temp = int(group)
        elif '+' in group: #group 2: 70+
            temp = 70
        else: #group 3: other. Store first number in age group
            temp = int(group.split('-')[0])

        if temp not in age_groups:
            age_groups.update({temp: 0})
        age_groups[temp] += case_num

    return age_groups

    #print the age groups in decending order
def print_by_age(results):
    print('年齡層\t 確診')
    print('------\t ----')
    for key, value in sorted(results.items(), reverse = True):
        if key < 5:
            print('{}\t{:>5}'.format(key, value))
        elif key == 70:
            print('{}+\t{:>5}'.format(key, value))
        else:
            print('{}-{}\t{:>5}'.format(key, key+5, value))

def sort_by_date(case_list): #TODO order by cases number
    #nested dictionarys.
    #days = {date1: {'本土案例': 0, '境外移入': 0},
    #        date2: {'本土案例': 0, '境外移入': 0}...}
    days = {}
    months = {}

    #counting
    for case in case_list:
        y2_m2_d2 = case.get('個案研判日') #year/month/day
        y1_m1 = y2_m2_d2[:-3] #year/month
        case_num = int(case.get('確定病例數'))

        if y2_m2_d2 not in days:
            days.update({y2_m2_d2: {'本土案例': 0, '境外移入': 0}})
        if y1_m1 not in months:
            months.update({y1_m1: {'本土案例': 0, '境外移入': 0}})

        #store the info '是否為境外移入' in seperate sub dictionarys   
        if case['是否為境外移入'] == '是':
            days[y2_m2_d2]['境外移入'] += case_num
            months[y1_m1]['境外移入'] += case_num
        else:
            days[y2_m2_d2]['本土案例'] += case_num
            months[y1_m1]['本土案例'] += case_num

    return months, days

#print the results of sort_by_day()
def print_by_date(months, days):
    #print months
    for y1_m1, value in months.items(): #y1_m1 = 2020/06
        y1, m1 = y1_m1.split('/')
        print('{}年{}月: [本土案例 {}\t境外移入 {}]'.format(
            y1, m1, value['本土案例'], value['境外移入']))
        print('-----------')
        #print days
        for y2_m2_d2, value in days.items(): #y2_m2_d2 = 2020/06/15
            y2_m2, d2 = y2_m2_d2[:-3], y2_m2_d2[-2:]
            if y1_m1 == y2_m2:
                print('{}日:  本土案例 {:>3}\t境外移入 {:>2}'.format(
                    d2, value['本土案例'], value['境外移入']))
        print('')

def summary_today(case_list):
    #get data for today from sort_by_date()
    _, day = sort_by_date(case_list)
    key, value = list(day.items())[0]
    total_case_num = value['本土案例'] + value['境外移入']
    print('{} 疫情資料\n---------------------'.format(key))
    print('總確診: {}\t[本土案例: {}  境外移入: {}]\n'.format(total_case_num, value['本土案例'], value['境外移入']))
    
    city_district = sort_by_location(case_list)
    print_by_location(city_district)
    age_groups = sort_by_age(case_list)
    print_by_age(age_groups)
            
def average_xdays(case_list, x):
    #count the average case number of x days
    l_sum, f_sum = 0, 0
    _, days = sort_by_date(case_list)
    for value in days.values():
        l_sum += value['本土案例']
        f_sum += value['境外移入']
    l_avg, f_avg = l_sum / x, f_sum / x
    t_avg = l_avg + f_avg
    
    #get date(yyyy/mm/dd) of first and last day
    first = (datetime.today() - timedelta(x)).strftime('%Y/%m/%d') 
    last = (datetime.today() - timedelta(1)).strftime('%Y/%m/%d')
    print('[{} - {}] {}天的平均確診數'.format(first, last, x))
    print('-----------------------------------------')
    print('每日平均確診: {:.2f}\t[本土案例: {:.2f}  境外移入: {:.2f}]\n'.format(t_avg, l_avg, f_avg))
    
    #get the x day average for each city
    print('各縣市\n------')
    city_district = sort_by_location(case_list)
    for key, value in city_district.items():
        c_avg = int(value['總共']) / x
        print('{}:\t{:>5.2f}'.format(key, c_avg))
    print('')

    #get the x day average for each age group
    age_groups = sort_by_age(case_list)
    for key, value in age_groups.items():
        value = round(value / x, 2)
        age_groups.update({key: value})
    print_by_age(age_groups)

def get_results(choice, data, first):
    ''' 
    get_results will handles user's choice with according funtions.
    It will print the results then prompt the user for whether to write
    the results in a txt file. Parament first is used to determine if the 
    function is ran for the first time.
    '''
    if choice == 1: #昨日疫情資料
        if first:
            input_date = (datetime.today() - timedelta(1)).strftime('%Y/%m/%d')
            data = util.get_subset(data, input_date)
        if data:
            summary_today(data)
        else:
            print('昨日資料尚未發布')
    elif choice == 2: #近x日平均數據
        if first:
            x = int(input('輸入(x): '))
            input_date = (datetime.today() - timedelta(x)).strftime('%Y/%m/%d')
            data = util.get_subset(data, input_date)
        average_xdays(data, x)
        util.write_to_txt(average_xdays, input_date, data, x)
    else:
        if first:
            #get a subset of data using user's input date 
            input_date = input('輸入日期 格式[yyyy/mm/dd] (查看所有歷史資料輸入 0): ')
            print('')
            if input_date != '0':
                data = util.get_subset(data, input_date)

        if data:
            if choice == 3: #縣市與鄉鎮
                results = sort_by_location(data)
                print_by_location(results)
            if choice == 4: #性別
                results = sort_by_gender(data)
                print_by_gender(results)
            if choice == 5: #年齡層
                results = sort_by_age(data)
                print_by_age(results)
            if choice == 6: #日期
                months, days = sort_by_date(data)
                print_by_date(months, days)
        else:
            print('無資料，檢查輸入日期有無誤。')

    if first and choice != 2:
        util.write_to_txt(get_results, input_date, choice, data, False)

def main():
    #get data and convert to json
    res = requests.get('https://od.cdc.gov.tw/eic/Day_Confirmation_Age_County_Gender_19CoV.json')
    data = res.json()

    while True:
        #choose content
        print('\n本資料集每日依系統固定排程更新一次，呈現截至前一日之統計資訊。')
        print('1 - 昨日疫情資料')
        print('2 - 近x日平均數據\n')
        print('依類別收尋資料:')
        print('3 - 縣市與鄉鎮')
        print('4 - 性別&總確診數')
        print('5 - 年齡層')
        print('6 - 日期')
        print('9 - 中斷程式')
        choice = int(input('輸入: '))
        if choice == 9:
            break

        get_results(choice, data, True)
    
if __name__ == '__main__':
    main()