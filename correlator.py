import csv
import numpy as np
import pandas as pd
from fuzzywuzzy import process
from fuzzywuzzy import fuzz

# https://www.shanelynn.ie/summarising-aggregation-and-grouping-data-in-python-pandas/

HTTP_LOG_FILE = "./data4.0/data4.0/GET_http.csv"
SQL_LOG_FILE = "./data4.0/data4.0/LOG_mysql.csv"

hlog = open(HTTP_LOG_FILE, 'r')
hlog_reader = pd.read_csv(HTTP_LOG_FILE) # csv.DictReader(hlog) # csv.reader(hlog, delimiter=',')
hlog_reader['payload'] = hlog_reader['payload'].astype(str) 

slog = open(SQL_LOG_FILE, 'r')
slog_reader = pd.read_csv(SQL_LOG_FILE) # csv.DictReader(slog) # csv.reader(slog, delimiter=',')
slog_reader['query'] = slog_reader['query'].astype(str) 

# print(hlog_reader.head())

hlog_grouptimestamp = hlog_reader.groupby(['timestamp'])

# print(hlog_grouptimestamp['payload'].head())

slog_grouptimestamp = slog_reader.groupby(['timestamp'])
# print(slog_grouptimestamp['query'].head())

# result = pd.concat([g[1].merge(categories, how='outer', on='ts') for g in [hlog_grouptimestamp, slog_grouptimestamp]])
# hlog_grouptimestamp.apply(Output=[process.extract(i, hlog_reader['payload'], limit=3) for i in slog_reader['query']])
# slog_grouptimestamp = {}

# print([i for i in slog_grouptimestamp.get_group(key) for key, item in slog_grouptimestamp)
# for row in slog_grouptimestamp.itertuples():
#     print((row.Index, row.query, row.query))

# result = pd.concat([hlog_grouptimestamp, slog_grouptimestamp], axis=1)
# print(result)

def get_similar(df):
    # print([srow['query'] for (skey, srow) in slog_grouptimestamp])
    # for skey, srow in slog_grouptimestamp.get_group(df['timestamp']).iterrows():
    #     print(srow['query'])
    # print([srow['query'] for skey, srow in slog_grouptimestamp.get_group(df['timestamp']).iterrows()] if df['timestamp'] in slog_grouptimestamp.groups else (0, 0))
    # res = process.extractOne(df['payload'], [i for (skey, srow) in slog_grouptimestamp for i in srow['query']])
    result = process.extractOne(df['payload'], {idx: el for idx, el in enumerate([srow['query'] for skey, srow in slog_grouptimestamp.get_group(df['timestamp']).iterrows()] if df['timestamp'] in slog_grouptimestamp.groups else [])}, score_cutoff=90)

    if result is not None:
        query, score, index = result
        sdata = slog_grouptimestamp.get_group(df['timestamp']).iloc[index,:] if df['timestamp'] in slog_grouptimestamp.groups else None
        print(type(df.to_frame()))
        print(type(sdata.to_frame()))
        print(pd.concat([df, sdata], axis=1, sort=False))
        input()
    # return res

for hkey, hrow in hlog_grouptimestamp:
    # print(hrow)
    # input()
    hrow.apply(get_similar, axis=1)
    # hrow['correlate'] = process.extractOne(hrow['payload'], [srow['query'] for skey, srow in slog_grouptimestamp.get_group(hrow['timestamp']).iterrows()] if hrow['timestamp'] in slog_grouptimestamp.groups else [])
#     for row in hrow['payload']:
#         print(row)
#         # hrow['correlate'] = process.extractOne(row, [srow['query'] for skey, srow in slog_grouptimestamp.get_group(hrow['timestamp']).iterrows()] if hrow['timestamp'] in slog_grouptimestamp.groups else [])
# #     # hrow.apply(Output=[process.extract(payload, [], limit=1) for (key, payload) in hrow['payload'].iteritems()])
#         input()

# for row in hlog_reader:
#     if row['timestamp'] not in hlog_grouptimestamp:
#         hlog_grouptimestamp[row['timestamp']] = []
#     hlog_grouptimestamp[row['timestamp']].append(row)

# for row in slog_reader:
#     if row['timestamp'] not in slog_grouptimestamp:
#         slog_grouptimestamp[row['timestamp']] = []
#     slog_grouptimestamp[row['timestamp']].append(row)

# keys = list(hlog_grouptimestamp.keys() | slog_grouptimestamp.keys())

# for k in keys:
#     print(len(hlog_grouptimestamp[k]))
#     input()
#     print(len(slog_grouptimestamp[k]))
#     input()
# np.corrcoef(
#     [hlog_grouptimestamp.get(x, 0) for x in keys],
#     [slog_grouptimestamp.get(x, 0) for x in keys])[0, 1]

# for c in correlated:
#     df = pd.DataFrame(c)
#     corr = df.corr()
#     print(corr)
# df = pd.DataFrame(correlated)
# corr = df.corr()
# print(corr)

# for row in slog_reader:
#     correlated[row['timestamp']]