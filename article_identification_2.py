# __author__      = "Bekah P Stein"

import pandas as pd
import numpy as np
from datetime import datetime
from datetime import date
import string
from nltk import word_tokenize, pos_tag

print("start:", datetime.now())

# fill in file names. There can be as many as you want, but they must be separated by a comma, like so
# headline_file_names = ['Official Headlines.xlsx', 'Official Headlines (1).xlsx', 'Official Headlines (2).xlsx']
headline_file_names = ['Official Headlines.xlsx']

# concatenating headlines files
headlines = pd.DataFrame()
for i in headline_file_names:
    file = pd.read_excel(i, sheet_name='Master Headlines')
    headlines = pd.concat([headlines, file], ignore_index=True)

# import other files
people = pd.read_csv('directors_and_super_names_current.csv', low_memory=False)
companies = pd.read_csv('merge_companies_2022-08-31.csv', low_memory=False)

# NOTE: if the code is calling affiliates which have been abbreviated to words or names (ex. corporation or Phoenix),
# you can add them to the bottom of the 5000 words list manually,
# then they will revert to their previous name (ex. including LLC)

companies['Strip 1'] = companies['Strip 1'].fillna('')

# make all files lowercase
people['FULLNAME'] = people['FULLNAME'].str.lower()
headlines['Title'] = headlines['Title'].str.lower()
headlines['Article Content'] = headlines['Article Content'].str.lower()

# strip random characters from Article Content
headlines['Article Content Clean'] = headlines['Article Content'].str.replace(';', "'", regex=False).str.\
    replace('<[^>]+>', ' ', regex=True).str.replace('\xa0', ' ', regex=True).str.replace('&#....', ' ', regex=True).\
    str.replace('&#...', ' ', regex=True).str.replace('.', '. ', regex=False).str.replace(',', ', ', regex=False)\
    .str.replace(" '", "'", regex=False)

# remove special characters in names from non english letters
remove = string.punctuation
remove = remove.replace("-", "").replace(".", "").replace("'", "")  # don't remove hyphens, periods, or apostrophes
people['FULLNAME'] = people['FULLNAME'].str.translate(str.maketrans('', '', remove))
# remove "dr." and "dr. " from names
people['FULLNAME'] = people['FULLNAME'].str.replace('dr. ', '', regex=False).replace('dr.', '', regex=False)

# get rid of extra white spaces
headlines['Article Content Clean'] = headlines['Article Content Clean'].replace(r'\s+', ' ', regex=True)

# nltk

# NN: noun, common, singular or mass
# NNP: noun, proper, singular
# NNPS: noun, proper, plural
# NNS: noun, common, plural

# tagging parts of speech to pull nouns and adjectives from headlines to get rid of excess words and verbs for better
# identification of company names and efficiency (fewer words to search through)

headlines['nouns'] = ''
j = 0
while j < len(headlines):
    ex = headlines['Title'][j]
    tokens = word_tokenize(ex)
    tag = pos_tag(tokens)
    # pull out nouns
    nouns = [a[0] for a in tag if a[1] == 'NNP' or a[1] == 'NNPS' or a[1] == 'NN' or a[1] == 'NNS' or a[1] == 'JJ'
             or a[1] == 'JJR' or a[1] == '']
    # make into "sentence" to search for company names
    mySeparator = " "
    x = mySeparator.join(nouns)
    headlines['nouns'].values[j] = x
    j = j+1

# do the same for article content
headlines['Article Content Clean nouns'] = ''
headlines['Article Content Clean'] = headlines['Article Content Clean'].fillna('')
j = 0
while j < len(headlines):
    ex = headlines['Article Content Clean'][j]
    tokens = word_tokenize(ex)
    tag = pos_tag(tokens)
    # pull out nouns
    nouns = [a[0] for a in tag if a[1] == 'NNP' or a[1] == 'NNPS' or a[1] == 'NN' or a[1] == 'NNS' or a[1] == 'JJ'
             or a[1] == 'JJR' or a[1] == '']
    # make into "sentence" to search for company names
    mySeparator = " "
    x = mySeparator.join(nouns)
    headlines['Article Content Clean nouns'].values[j] = x
    j = j+1


split_nouns = headlines['nouns'].str.split()
list_nouns = split_nouns.sum()
df_nouns = pd.DataFrame(list_nouns)
sum_nouns = df_nouns.value_counts()


# add spaces at beginning and end of nouns, so we can search for company names and not get parts of words
headlines['nouns'] = ' ' + headlines['nouns'] + ' '
headlines['Title'] = ' ' + headlines['Title'] + ' '

# search article nouns for company names
headlines['Company Names (tag)'] = np.empty((len(headlines), 0)).tolist()
headlines['Company ISIN'] = np.empty((len(headlines), 0)).tolist()
headlines['People Names'] = np.empty((len(headlines), 0)).tolist()
headlines['People Individual IDs'] = np.empty((len(headlines), 0)).tolist()

k = 0
while k < len(companies):
    temp1 = headlines.loc[headlines['nouns'].str.contains((' ' + companies['Strip 1'][k] + ' '), case=False,
                                                          regex=False)]
    i = 0
    if len(temp1) > 0:
        while i < len(temp1):
            if any(companies['Strip 1'][k] in sub for sub in headlines['Company Names (tag)'][temp1.index[i]]):
                # already in list, so do nothing
                nothing = 'nothing'
            else:
                headlines['Company Names (tag)'][temp1.index[i]] = headlines['Company Names (tag)'][temp1.index[i]] + \
                                                                   [companies['ISSUER_NAME'][k] + '(' +
                                                                    companies['Strip 1'][k] + ')']
                headlines['Company ISIN'][temp1.index[i]] = (headlines['Company ISIN'][temp1.index[i]] +
                                                             [companies['ISSUER_ISIN'][k]])
            i = i+1
    k = k+1


# search article nouns for names of individuals
k = 0
while k < len(people):
    temp1 = headlines.loc[headlines['Title'].str.contains((' ' + people['FULLNAME'][k] + ' '), case=False, regex=False)]
    i = 0
    if len(temp1) > 0:
        while i < len(temp1):
            if any(people['FULLNAME'][k] in sub for sub in headlines['People Names'][temp1.index[i]]):
                # already in list, so do nothing
                nothing = 'nothing'
            else:
                headlines['People Names'][temp1.index[i]] = headlines['People Names'][temp1.index[i]] + \
                                                                   [people['FULLNAME'][k]]
                headlines['People Individual IDs'][temp1.index[i]] = (headlines['People Individual IDs'][temp1.index[i]]
                                                                      + [people['INDIVIDUAL_ID'][k]])
            i = i+1
    k = k+1


# search article nouns for brand names
companies['Strip 13'] = companies['Strip 13'].astype(str)
companies['ISSUER_NAME'] = companies['ISSUER_NAME'].astype(str)
k = 0
while k < len(companies):
    temp1 = headlines.loc[headlines['nouns'].str.contains((' ' + companies['Strip 13'][k] + ' '), case=False)]
    i = 0
    if len(temp1) > 0:
        while i < len(temp1):
            if any(companies['Strip 13'][k] in sub for sub in headlines['Company Names (tag)'][temp1.index[i]]):
                # already in list, so do nothing
                nothing = 'nothing'
            else:
                headlines['Company Names (tag)'][temp1.index[i]] = headlines['Company Names (tag)'][temp1.index[i]] + \
                                                                   [companies['ISSUER_NAME'][k] + '(' +
                                                                    companies['Strip 13'][k] + ')']
                headlines['Company ISIN'][temp1.index[i]] = (headlines['Company ISIN'][temp1.index[i]] +
                                                             [companies['ISSUER_ISIN'][k]])

            i = i+1
    k = k+1


# search article content (Article Content Clean nouns) for company names
# replace nan with ''
headlines['Article Content Clean nouns'] = headlines['Article Content Clean nouns'].fillna('')
k = 0
while k < len(companies):
    temp1 = headlines.loc[headlines['Article Content Clean nouns'].str.contains((' ' + companies['Strip 1'][k] + ' '),
                                                                                case=False, regex=False)]
    i = 0
    if len(temp1) > 0:
        while i < len(temp1):
            if any(companies['Strip 1'][k] in sub for sub in headlines['Company Names (tag)'][temp1.index[i]]):
                # already in list, so do nothing
                nothing = 'nothing'
            else:
                headlines['Company Names (tag)'][temp1.index[i]] = headlines['Company Names (tag)'][temp1.index[i]] + \
                                                                   [companies['ISSUER_NAME'][k] + '(' +
                                                                    companies['Strip 1'][k] + ')']
                headlines['Company ISIN'][temp1.index[i]] = (headlines['Company ISIN'][temp1.index[i]] +
                                                             [companies['ISSUER_ISIN'][k]])

            i = i+1
    k = k+1


# search article content (Article Content Clean nouns) for people names
k = 0
while k < len(people):
    temp1 = headlines.loc[headlines['Article Content Clean nouns'].str.contains((' ' + people['FULLNAME'][k] + ' '),
                                                                                case=False, regex=False)]
    i = 0
    if len(temp1) > 0:
        while i < len(temp1):
            if any(people['FULLNAME'][k] in sub for sub in headlines['People Names'][temp1.index[i]]):
                # already in list, so do nothing
                nothing = 'nothing'
            else:
                headlines['People Names'][temp1.index[i]] = headlines['People Names'][temp1.index[i]] + \
                                                                   [people['FULLNAME'][k]]
                headlines['People Individual IDs'][temp1.index[i]] = (headlines['People Individual IDs'][temp1.index[i]]
                                                                      + [people['INDIVIDUAL_ID'][k]])

            i = i+1
    k = k+1


# search article content (Article Content Clean nouns) for brand names
k = 0
while k < len(companies):
    temp1 = headlines.loc[headlines['Article Content Clean nouns'].str.contains((' ' + companies['Strip 13'][k]
                                                                                 + ' '), case=False, regex=False)]
    i = 0
    if len(temp1) > 0:
        while i < len(temp1):
            if any(companies['Strip 13'][k] in sub for sub in headlines['Company Names (tag)'][temp1.index[i]]):
                # already in list, so do nothing
                nothing = 'nothing'
            else:

                headlines['Company Names (tag)'][temp1.index[i]] = headlines['Company Names (tag)'][temp1.index[i]] + \
                                                                   [companies['ISSUER_NAME'][k] + '(' +
                                                                    companies['Strip 13'][k] + ')']
                headlines['Company ISIN'][temp1.index[i]] = (headlines['Company ISIN'][temp1.index[i]] +
                                                             [companies['ISSUER_ISIN'][k]])

            i = i+1
    k = k+1


headlines_simple = headlines[['Date', 'Title', 'URL', 'Image', 'Source', 'Category', 'Article Content Clean',
                              'Company Names (tag)', 'Company ISIN', 'People Names', 'People Individual IDs']].copy()

# save tagged headlines
headlines_simple.to_csv(('tagged_headlines_' + str(date.today()) + '.csv'), index=False)

print("end all:", datetime.now())
companies['length'] = companies['Strip 13'].str.len()
stuff = companies.sort_values(by=['length', 'Strip 1', 'Strip 13'])
stuff = stuff[['ISSUER_ISIN', 'ISSUER_NAME', 'ISSUERID', 'ISSUER_TICKER', 'Strip 1', 'Strip 13', 'length']]
stuff = stuff.sort_values(by=['length', 'Strip 1', 'Strip 13'])
stuff = stuff.dropna(subset=['Strip 13']).reset_index(drop=True)
