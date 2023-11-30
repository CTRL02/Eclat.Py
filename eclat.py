import pandas as pd
from collections import defaultdict
from collections import Counter
from itertools import chain, combinations

min_supp = 3
min_conf = 0.7
rules_list = []
strong_list = []
lift_list = []


# def GetLift(dataframe, items, delimit):
#     leftItems = []
#     for i in range(delimit):
#         leftItems.append(items[i])
#     result = [item for item in items if item not in leftItems]
#     # Your formula here


def getLift(dataframe, items):
    num_rows = dataframe.shape[0]
    leftr = items[0]
    right = items[1]
    union = float(Getsupp(dataframe, items) / num_rows)
    result1 = float(Getsupp(dataframe, leftr) / num_rows)
    result2 = float(Getsupp(dataframe, right) / num_rows)
    return float(union / result1 * result2)


def generate_subsets(items):
    subsets = []
    for i in range(1, len(items)):
        subsets.extend(combinations(items, i))
    return subsets


def generate_association_rules(items):
    subsets = generate_subsets(items)
    for subset in subsets:
        antecedent = list(subset)
        consequent = list(set(items) - set(subset))
        rule = (antecedent, consequent)
        rules_list.append(rule)


def Getsupp(dataframe, items):
    listItem = []
    if isinstance(items, tuple):
        listItem = [item for sublist in items for item in sublist]
    else:
        listItem = items

    # print(listItem)
    all_trans = []
    supp = 0
    for item in listItem:
        for tid in range(len(dataframe)):
            if dataframe[item][tid] != 0:
                all_trans.append(dataframe[item][tid])
    trans_counter = Counter(all_trans)
    # print(trans_counter)
    for value in trans_counter.values():
        if value == len(listItem):
            supp += 1
    return supp


def eclat(dataframe, minsup, minconf):
    def eclat_recursive(prefix, items):
        frequent_itemsets = []
        for i, item in enumerate(items):
            # print(i, item)
            new_prefix = prefix + [item]
            # print(new_prefix)
            support = Getsupp(dataframe, new_prefix)

            if support >= minsup:
                frequent_itemsets.append((new_prefix, support))

                next_items = items[i + 1:]
                # print(items[i + 1:])
                if len(next_items) > 0:
                    frequent_itemsets.extend(eclat_recursive(new_prefix, next_items))

        return frequent_itemsets

    items = list(dataframe.columns)
    frequent_itemsets = eclat_recursive([], items)
    return frequent_itemsets


def convert_to_vertical(dataframe):
    inverted_index = defaultdict(list)
    for index, row in dataframe.iterrows():
        transaction_id = row.iloc[0]
        items = row.iloc[1:]
        for item in items:
            if pd.notna(item):
                item = str(item).strip()
                letters = [letter for letter in item if letter.strip() and letter != ',']
                for letter in letters:
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


file_path = 'Horizontal_Format.xlsx'
df = pd.read_excel(file_path, engine='openpyxl')
headers = df.columns.tolist()
vertical_df = []
if headers[0].lower() == "tid":
    vertical_df = convert_to_vertical(df)

frequent_items = eclat(vertical_df, min_supp, min_conf)
for item in frequent_items:
    if len(item[0]) >= 2:
        generate_association_rules(item[0])

for item in rules_list:
    allItems = Getsupp(vertical_df, item)
    left = Getsupp(vertical_df, item[0])
    if float(allItems / left) >= min_conf:
        strong_list.append(item)
        lift = getLift(vertical_df, item)
        lift_list.append(lift)

print("Frequent items are:    ", frequent_items)
print("The Association rules are: ", rules_list)
print("The Strong rules are: ", strong_list)
print("The associated lift values for the strong rules are: ", lift_list)

