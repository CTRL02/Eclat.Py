import pandas as pd
from collections import defaultdict
from collections import Counter
from itertools import chain, combinations

sup = input("Enter Sup   ")
conf = input("Enter Conf  ")
min_supp = int(sup)
min_conf = float(conf)
rules_list = []
strong_list = []


# all_confidence = []


def getLift(dataframe, items):
    max_transactions = 0
    for item in dataframe:
        if max(dataframe[item]) > max_transactions:
            max_transactions = max(dataframe[item])
    leftr = items[0]
    right = items[1]
    union = float(Getsupp(dataframe, items) / max_transactions)
    result1 = float(Getsupp(dataframe, leftr) / max_transactions)
    result2 = float(Getsupp(dataframe, right) / max_transactions)
    return float(union / (result1 * result2))


# to print all possible subsets [('A',), ('B',), ('C',), ('A', 'B'), ('A', 'C'), ('B', 'C')]
def generate_subsets(items):
    subsets = []
    for i in range(1, len(items)):
        subsets.extend(combinations(items, i))
    return subsets


# take subsets and generate my association rules
def generate_association_rules(items):
    subsets = generate_subsets(items)
    for subset in subsets:
        atecde = list(subset)
        conseq = list(set(items) - set(subset))
        rule = (atecde, conseq)
        rules_list.append(rule)


def Getsupp(dataframe, items):
    listItem = []
    if isinstance(items, tuple):
        listItem = [item for sublist in items for item in sublist]
    else:
        listItem = items

    all_trans = []
    supp = 0
    # ['a','b','c']
    for item in listItem:
        # [(1,2,4), (1,2,3), (1,3,2)] the transactions they appeared in
        for tid in range(len(dataframe)):
            if dataframe[item][tid] != 0:
                all_trans.append(dataframe[item][tid])
    trans_counter = Counter(all_trans)
    # print(trans_counter)
    for value in trans_counter.values():
        # if transaction id counter same as length of an item then they appeared together in this transaction
        if value == len(listItem):
            supp += 1
    return supp


def eclat(dataframe, minsup, minconf):
    def eclat_recursive(prefix, items):
        frequent_itemsets = []
        for i, item in enumerate(items):
            new_prefix = prefix + [item]
            support = Getsupp(dataframe, new_prefix)

            if support >= minsup:
                frequent_itemsets.append((new_prefix, support))

                next_items = items[i + 1:]
                if len(next_items) > 0:
                    frequent_itemsets.extend(eclat_recursive(new_prefix, next_items))

        return frequent_itemsets

    items = list(dataframe.columns)
    frequent_itemsets = eclat_recursive([], items)
    return frequent_itemsets


def fixVertical(dataframe):
    inverted_index = defaultdict(list)

    for index, row in dataframe.iterrows():
        current_item = str(row.iloc[0])
        transaction_ids = str(row.iloc[1]).split(',')
        for transaction_id in transaction_ids:
            if pd.notna(current_item) and pd.notna(transaction_id):
                inverted_index[current_item].append(transaction_id.strip())
                # print(current_item)
                # print(inverted_index[current_item])

    vertical_dataframe = pd.DataFrame.from_dict(inverted_index, orient='index')
    vertical_dataframe = vertical_dataframe.transpose().fillna(0).astype('int')
    return vertical_dataframe


def convert_to_vertical(dataframe):
    inverted_index = defaultdict(list)
    letters = []
    for index, row in dataframe.iterrows():
        # tid 1
        transaction_id = row.iloc[0]
        # monkey
        items = row.iloc[1:]
        for item in items:

            if pd.notna(item):
                item = str(item).strip()
                # print(item)
                # get each letter from monkey
                string_list = item.split(',')
                string_list = [s.strip() for s in string_list]
                # print(string_list)
                for letter in string_list:
                    # print(letter)
                    found = False
                    for tid in inverted_index[letter]:
                        if tid == transaction_id:
                            found = True
                    if not found:
                        inverted_index[letter].append(transaction_id)
                    # print(letter, ": ", inverted_index[letter])
    vertical_dataframe = pd.DataFrame.from_dict(inverted_index, orient='index')
    vertical_dataframe = vertical_dataframe.transpose().fillna(0).astype(int)
    return vertical_dataframe


file_path = 'horiTest.xlsx'
df = pd.read_excel(file_path, engine='openpyxl')
df = df.dropna(how='all')
print(df)
headers = df.columns.tolist()
vertical_df = []
if headers[0].lower() == "tid":
    vertical_df = convert_to_vertical(df)
else:
    vertical_df = fixVertical(df)

print("Our vertical data:   ")
print(vertical_df)
frequent_items = eclat(vertical_df, min_supp, min_conf)
print("Our Frequent items:     ")
print(frequent_items)
# print("Our frequent items:   ")
# print(frequent_items)
for item in frequent_items:
    if len(item[0]) >= 2:
        generate_association_rules(item[0])

print("Our Association rules are:   ")
print(rules_list)
for item in rules_list:
    allItems = Getsupp(vertical_df, item)
    left = Getsupp(vertical_df, item[0])
    # print(item, ": its confidence value:  ", float(allItems / left))
    # all_confidence.append(float(allItems / left))
    if float(allItems / left) >= min_conf:
        strong_list.append(item)

print("The Strong rules are: ", strong_list)
new_list = []
for item in rules_list:
    reversed_item = (item[1], item[0])
    if reversed_item not in new_list:
        new_list.append(item)
#
for item in new_list:
    if getLift(vertical_df, item) > 1:
        print(item, "is dependent and +ve correlated with lift value:    ", getLift(vertical_df, item))
    elif getLift(vertical_df, item) < 1:
        print(item, "is dependent and -ve correlated with lift value:    ", getLift(vertical_df, item))
    else:
        print(item, "is independent with lift value:    ", getLift(vertical_df, item))
