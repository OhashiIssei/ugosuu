def split_with_max_number(list:list,max_num:int):
    parent_list_num = len(list)//max_num
    new_list_list = []
    for num in range(parent_list_num+1):
        start = num*max_num
        end = min((num+1)*max_num,len(list))
        if start == end:break
        new_list_list.append(list[start:end])
    return new_list_list


# print(split_with_max_number([1,2,3,4,5,6,7,8,9,10],3))