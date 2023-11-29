import pandas as pd
from collections import defaultdict
from collections import Counter

min_supp = 2
min_conf = 0.7


def Getsupp(dataframe, items):
    all_trans = []
    supp = 0
    for item in items:
        for tid in range(len(dataframe)):
            if dataframe[item][tid] != 0:
                all_trans.append(dataframe[item][tid])
    trans_counter = Counter(all_trans)
    # print(trans_counter)
    for value in trans_counter.values():
        if value == len(items):
            supp += 1
    return supp


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
print(df)
vertical_df = convert_to_vertical(df)
print(vertical_df)
print("\n")
print(Getsupp(vertical_df, ['O', 'N']))
