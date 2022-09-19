# __author__      = "Bekah P Stein"

import pandas as pd
import numpy as np
from datetime import datetime
from datetime import date
import string
import re


# NOTE: if the code is calling "companies" which have been abbreviated to words or names (ex. corporation or Phoenix),
# you can add them to the bottom of the 5000 words list manually,
# then they will revert to their previous name (ex. including LLC)

# import files
print("start:", datetime.now())
companies = pd.read_csv('company_names_ISIN.csv', low_memory=False)
brands = pd.read_csv('multinationals_affiliates_2020_edit.csv', low_memory=False)

# 5000 words
common_words = pd.read_excel('5000_words.xlsx')
common_words = common_words.rename(columns={'Word': 'a'})

# make all files lowercase
companies['ISSUER_NAME'] = companies['ISSUER_NAME'].str.lower()


# strip extra spaces off front and back for those that have it
common_words_str = common_words.astype('str')
common_words_str['a'] = common_words_str['a'].str.strip()

# add them back on to all of them so don't get parts of words
common_words_str['a'] = ' ' + common_words_str['a'] + ' '

# simplify names of companies for searching
# get rid of punctuation because it messes with the replace function (because of reg ex)


remove = string.punctuation
# don't remove hyphens, &, or question marks (in some company names)
remove = remove.replace("-", "").replace("?", "").replace("&", "")
pattern = r"[{}]".format(remove)
companies['no punctuation'] = ''
m = 0
while m < len(companies):
    companies['no punctuation'][m] = re.sub(pattern, '', companies['ISSUER_NAME'][m])
    m = m+1

# Check the last word multiple times, and step back if needed

# initiate w/o_The to no punctuation
companies['w/o_The'] = np.empty((len(companies), 0)).tolist()
# get rid of "The"s at the beginning by pulling first word and checking if it is "the"
# pull first word
temp2 = companies['no punctuation'].str.partition()
# first word:
companies['"The"_Check'] = temp2[0]
# rest of company name w/o first word
companies['"The"_Check_rem'] = temp2[2]
for y, row in companies.iterrows():
    if row['"The"_Check'] == 'the':
        row['w/o_The'] = row['"The"_Check_rem']
    else:
        row['w/o_The'] = row['no punctuation']

# now want to check if last words are the ones we want to remove
# pull last word
companies['Strip 1'] = np.empty((len(companies), 0)).tolist()
temp1 = companies['w/o_The'].str.rpartition()
# need to pad temp with spaces for searching and not getting parts of words
companies['first1'] = temp1[0] + ' '
companies['last1'] = temp1[2] + ' '
# pull last word a second time
temp2 = companies['first1'].str.strip().str.rpartition()
companies['first2'] = temp2[0] + ' '
companies['last2'] = temp2[2] + ' '

for x, row in companies.iterrows():
    if row['last1'] == 'plc ' or row['last1'] == 'inc ' or row['last1'] == 'llc ' or row['last1'] == 'corp ' or \
            row['last1'] == 'ltd ' or row['last1'] == 'co ' or row['last1'] == 'coltd ' or row['last1'] == 'publ ' or \
            row['last1'] == 'tbk ' or row['last1'] == 'ka ' or row['last1'] == 'bm ' or row['last1'] == 'spa ' or \
            row['last1'] == 'nv ' or row['last1'] == 'sa ' or row['last1'] == 'se ' or row['last1'] == 'oyj ' or \
            row['last1'] == 'corporation ' or row['last1'] == 'enterprises ' or row['last1'] == 'industry ' or \
            row['last1'] == 'industries ' or row['last1'] == 'limited ' or row['last1'] == 'holdings ' or row['last1'] \
            == 'company ' or row['last1'] == 'international ' or row['last1'] == 'enterprises ' or row['last1'] == \
            'systems ' or row['last1'] == 'wholesale ' or row['last1'] == 'group ' or row['last1'] == 'wholesale ' \
            or row['last1'] == 'holdingsinc ' or row['last1'] == 'holdings ':
        row['Strip 1'] = row['first1']
        # need to strip extra spaces off some company names
        row['Strip 1'] = row['Strip 1'].strip()
        temp1_count = common_words_str['a'].str.contains(' ' + row['Strip 1'] + ' ', regex=False).sum()
        if temp1_count > 0:
            # if the company names after stripping can be found in the common word list - add back
            row['Strip 1'] = row['w/o_The']
    else:
        row['Strip 1'] = row['w/o_The']

for x, row in companies.iterrows():
    if row['last2'] == 'plc ' or row['last2'] == 'inc ' or row['last2'] == 'llc ' or row['last2'] == 'corp ' or \
            row['last2'] == 'ltd ' or row['last2'] == 'co ' or row['last2'] == 'coltd ' or row['last2'] == 'publ ' \
            or row['last2'] == 'tbk ' or row['last2'] == 'ka ' or row['last2'] == 'bm ' or row['last2'] == 'ag ' \
            or row['last2'] == 'spa ' or row['last2'] == 'nv ' or row['last2'] == 'se ' or row['last2'] == 'oyj ' \
            or row['last2'] == 'holdings ':
        # or row['last2'] == 'public joint stock '  or row['last2'] == 'p l c'
        row['Strip 1'] = row['first2']
        # need to strip extra spaces off some company names
        row['Strip 1'] = row['Strip 1'].strip()
        temp2_count = common_words_str['a'].str.contains(' ' + row['Strip 1'] + ' ').sum()
        if temp2_count > 0:
            # if the company names after stripping can be found in the common word list - add back
            row['Strip 1'] = row['first1']

# replace p l c  and public joint stock with ''
companies['Strip 1'] = companies['Strip 1'].str.replace("p l c", '').replace("public joint stock", '')

# after taking all the extra things off, want to strip any excess spaces
companies['Strip 1'] = companies['Strip 1'].str.strip()
print("start:", datetime.now())

# take off extra spaces (add back later to have consistency and able to search for words, and not get parts of words)
companies['Strip 1'] = companies['Strip 1'].str.strip()

# list of company names that are part of 5000 most common words - if this is working correctly, there should be none
L = 0
a = 0
common_company_names = pd.DataFrame(index=range(1000), columns=range(2))
common_company_names = common_company_names.rename(columns={0: 'names', 1: 'OG'})
while L < len(companies):
    temp1 = common_words_str.loc[common_words_str['a'].str.contains((' ' + companies['Strip 1'][L] + ' '), regex=False)]
    i = 0
    if len(temp1) > 0:
        while i < len(temp1):
            common_company_names['names'][a] = [companies['Strip 1'][L] + ' (name index:' + str(L) + ')']
            companies['Strip 1'][L] = companies['w/o_The'][L]  # reset the Strip 1 company names to not be common words
            common_company_names['OG'][a] = companies['ISSUER_NAME'][L]
            i = i+1
            a = a+1
    L = L+1
common_company_names = common_company_names.dropna()
print("end:", datetime.now())

# nltk

# NN: noun, common, singular or mass
# NNP: noun, proper, singular
# NNPS: noun, proper, plural
# NNS: noun, common, plural


# strip all spaces off both sides of company names after simplifying them
# companies['Strip 1'] = companies['Strip 1'].str.strip()


# Want to incorporate brands
# simple version of brands
brands_sim = brands[['Parent MNE', 'Affiliate Name']]
brands_sim = brands_sim.rename(columns={'Parent MNE': 'name', 'Affiliate Name': 'affiliate'})


# simplify new names like we did with other company names
# make new company names lowercase

brands_sim['name'] = brands_sim['name'].str.lower()
brands_sim['affiliate'] = brands_sim['affiliate'].str.lower()
brands_sim['affiliate'] = brands_sim['affiliate'].fillna('')

# simplify names of companies for searching
# get rid of punctuation because it messes with the replace function (because of reg ex)
remove = string.punctuation
# don't remove hyphens, &, or question marks (in some company names)
remove = remove.replace("-", "").replace("?", "").replace("&", "")
pattern = r"[{}]".format(remove)
brands_sim['no punctuation2'] = ''
m = 0
while m < len(brands_sim):
    brands_sim['no punctuation2'][m] = re.sub(pattern, '', brands_sim['name'][m])
    m = m+1

# initiate w/o_The to no punctuation
brands_sim['w/o_The2'] = np.empty((len(brands_sim), 0)).tolist()
# get rid of "The"s at the beginning by pulling first word and checking if it is "the"
# pull first word
temp22 = brands_sim['no punctuation2'].str.partition()
# first word:
brands_sim['"The"_Check2'] = temp22[0]
# rest of company name w/o first word
brands_sim['"The"_Check_rem2'] = temp22[2]
for y, row in brands_sim.iterrows():
    if row['"The"_Check2'] == 'the':
        row['w/o_The2'] = row['"The"_Check_rem2']
    else:
        row['w/o_The2'] = row['no punctuation2']

# now want to check if last words are the ones we want to remove
# pull last word
brands_sim['Strip 12'] = np.empty((len(brands_sim), 0)).tolist()
temp12 = brands_sim['w/o_The2'].str.rpartition()
# need to pad temp with spaces for searching and not getting parts of words
brands_sim['first12'] = temp12[0] + ' '
brands_sim['last12'] = temp12[2] + ' '
# pull last word a second time
temp22 = brands_sim['first12'].str.strip().str.rpartition()
brands_sim['first22'] = temp22[0] + ' '
brands_sim['last22'] = temp22[2] + ' '

for x, row in brands_sim.iterrows():
    if row['last12'] == 'the ' or row['last12'] == 'plc ' or row['last12'] == 'llc ' or row['last12'] == 'inc ' or \
            row['last12'] == 'corp ' or row['last12'] == 'ltd ' or row['last12'] == 'co ' or row['last12'] == 'coltd ' \
            or row['last12'] == 'publ ' or row['last12'] == 'tbk ' or row['last12'] == 'ka ' or row['last12'] == 'bm ' \
            or row['last12'] == 'spa ' or row['last12'] == 'nv ' or row['last12'] == 'sa ' or row['last12'] == 'se ' \
            or row['last12'] == 'oyj ' or row['last12'] == 'corporation ' or row['last12'] == 'enterprises ' or \
            row['last12'] == 'industry ' or row['last12'] == 'industries ' or row['last12'] == 'limited ' or \
            row['last12'] == 'holdings ' or row['last12'] == 'company ' or row['last12'] == 'international ' or \
            row['last12'] == 'enterprises ' or row['last12'] == 'systems ' or \
            row['last12'] == 'wholesale ' or row['last12'] == 'group ':
        row['Strip 12'] = row['first12']
        # need to strip extra spaces off some company names
        row['Strip 12'] = row['Strip 12'].strip()
        temp1_count2 = common_words_str['a'].str.contains(' ' + row['Strip 12'] + ' ', regex=False).sum()
        if temp1_count2 > 0:
            # if the company names after stripping can be found in the common word list - add back
            row['Strip 12'] = row['w/o_The2']
    else:
        row['Strip 12'] = row['w/o_The2']

for x, row in brands_sim.iterrows():
    if row['last22'] == 'the ' or row['last22'] == 'plc ' or row['last22'] == 'llc ' or row['last22'] == 'inc ' or \
            row['last22'] == 'corp ' or row['last22'] == 'ltd ' or row['last22'] == 'co ' or row['last22'] == 'coltd '\
            or row['last22'] == 'publ ' or row['last22'] == 'tbk ' or row['last22'] == 'ka ' or row['last22'] == 'bm ' \
            or row['last22'] == 'ag ' or row['last22'] == 'spa ' or row['last22'] == 'nv ' \
            or row['last22'] == 'se ' or row['last22'] == 'oyj ':
        # or row['last2'] == 'public joint stock '  or row['last2'] == 'p l c'
        row['Strip 12'] = row['first22']
        # need to strip extra spaces off some company names
        row['Strip 12'] = row['Strip 12'].strip()
        temp2_count2 = common_words_str['a'].str.contains(' ' + row['Strip 12'] + ' ').sum()
        if temp2_count2 > 0:
            # if the company names after stripping can be found in the common word list - add back
            row['Strip 12'] = row['first12']

# replace p l c  and public joint stock with ''
brands_sim['Strip 12'] = brands_sim['Strip 12'].str.replace("p l c", '').replace("public joint stock", '')


# take off extra spaces (add back later to have consistency and able to search for words, and not get parts of words)
brands_sim['Strip 12'] = brands_sim['Strip 12'].str.strip()

# list of company names that are part of 5000 most common words
L = 0
a = 0
common_company_names2 = pd.DataFrame(index=range(1000), columns=range(2))
common_company_names2 = common_company_names2.rename(columns={0: 'names', 1: 'OG'})
while L < len(brands_sim):
    temp14 = common_words_str.loc[common_words_str['a'].str.contains((' ' + brands_sim['Strip 12'][L] + ' '),
                                                                     case=False)]
    i = 0
    if len(temp14) > 0:
        while i < len(temp14):
            common_company_names2['names'][a] = [brands_sim['Strip 12'][L] + '(name index:' + str(L) + ')']
            # reset the Strip 12 company names to not be common words
            brands_sim['Strip 12'][L] = brands_sim['w/o_The2'][L]
            common_company_names2['OG'][a] = brands_sim['name'][L]
            i = i+1
            a = a+1
    L = L+1
common_company_names2 = common_company_names2.dropna()

# now we need to do the same to affiliates

# simplify names of companies for searching
# get rid of punctuation because it messes with the replace function (because of reg ex)
remove = string.punctuation
# don't remove hyphens, &, or question marks (in some company names)
remove = remove.replace("-", "").replace("?", "").replace("&", "")

pattern = r"[{}]".format(remove)
brands_sim['no punctuation3'] = ''
m = 0
while m < len(brands_sim):
    brands_sim['no punctuation3'][m] = re.sub(pattern, '', brands_sim['affiliate'][m])
    m = m+1

# initiate w/o_The to no punctuation
brands_sim['w/o_The3'] = np.empty((len(brands_sim), 0)).tolist()
# get rid of "The"s at the beginning by pulling first word and checking if it is "the"
# pull first word
temp23 = brands_sim['no punctuation3'].str.partition()
# first word:
brands_sim['"The"_Check3'] = temp23[0]
# rest of company name w/o first word
brands_sim['"The"_Check_rem3'] = temp23[2]
for y, row in brands_sim.iterrows():
    if row['"The"_Check3'] == 'the':
        row['w/o_The3'] = row['"The"_Check_rem3']
    else:
        row['w/o_The3'] = row['no punctuation3']

# now want to check if last words are the ones we want to remove
# pull last word
brands_sim['Strip 13'] = np.empty((len(brands_sim), 0)).tolist()
temp13 = brands_sim['w/o_The3'].str.rpartition()
# need to pad temp with spaces for searching and not getting parts of words
brands_sim['first13'] = temp13[0] + ' '
brands_sim['last13'] = temp13[2] + ' '
# pull last word a second time
temp23 = brands_sim['first13'].str.strip().str.rpartition()
brands_sim['first23'] = temp23[0] + ' '
brands_sim['last23'] = temp23[2] + ' '

for x, row in brands_sim.iterrows():
    if row['last13'] == 'the ' or row['last13'] == 'plc ' or row['last13'] == 'llc ' or row['last13'] == 'inc ' or \
            row['last13'] == 'corp ' or row['last13'] == 'ltd ' or row['last13'] == 'co ' or row['last13'] == 'coltd ' \
            or row['last13'] == 'publ ' or row['last13'] == 'tbk ' or row['last13'] == 'ka ' or row['last13'] == 'bm '\
            or row['last13'] == 'spa ' or row['last13'] == 'nv ' or row['last13'] == 'sa ' or row['last13'] == 'se ' \
            or row['last13'] == 'oyj ' or row['last13'] == 'corporation ' or row['last13'] == 'enterprises ' or \
            row['last13'] == 'industry ' or row['last13'] == 'industries ' or row['last13'] == 'limited ' or \
            row['last13'] == 'holdings ' or row['last13'] == 'company ' or\
            row['last13'] == 'international ' or row['last13'] == 'enterprises ' or row['last13'] == 'systems ' or \
            row['last13'] == 'wholesale ' or row['last13'] == 'group ' or row['last13'] == 'bv':
        row['Strip 13'] = row['first13']
        row['Strip 13'] = row['Strip 13'].strip()
        temp1_count3 = common_words_str['a'].str.contains(' ' + row['Strip 13'] + ' ', regex=False).sum()
        if temp1_count3 > 0:
            # if the company names after stripping can be found in the common word list - add back
            row['Strip 13'] = row['w/o_The3']
    else:
        row['Strip 13'] = row['w/o_The3']

for x, row in brands_sim.iterrows():
    if row['last23'] == 'the ' or row['last23'] == 'plc ' or row['last23'] == 'llc ' or row['last23'] == 'inc ' or \
            row['last23'] == 'corp ' or row['last23'] == 'ltd ' or row['last23'] == 'co ' or row['last23'] == 'coltd ' \
            or row['last23'] == 'publ ' or row['last23'] == 'tbk ' or row['last23'] == 'ka ' or row['last23'] == 'bm '\
            or row['last23'] == 'ag ' or row['last23'] == 'spa ' or row['last23'] == 'nv ' \
            or row['last23'] == 'se ' or row['last23'] == 'oyj ':
        # or row['last2'] == 'public joint stock '  or row['last2'] == 'p l c'
        row['Strip 13'] = row['first23']
        row['Strip 13'] = row['Strip 13'].strip()
        temp2_count3 = common_words_str['a'].str.contains(' ' + row['Strip 13'] + ' ', regex=False).sum()
        if temp2_count3 > 0:
            # if the company names after stripping can be found in the common word list - add back
            row['Strip 13'] = row['first13']

# replace p l c  and public joint stock with ''
brands_sim['Strip 13'] = brands_sim['Strip 13'].str.replace("p l c", '').replace("public joint stock", '')

# ToDo: fix common_company_names3 - should be empty so filter on brands not working

# take off extra spaces (add back later to have consistency and able to search for words, and not get parts of words)
brands_sim['Strip 13'] = brands_sim['Strip 13'].str.strip()
# list of company names that are part of 5000 most common words - should be empty
L = 0
a = 0
common_company_names3 = pd.DataFrame(index=range(1000), columns=range(2))
common_company_names3 = common_company_names3.rename(columns={0: 'names', 1: 'OG'})
while L < len(brands_sim):
    temp15 = common_words_str.loc[common_words_str['a'].str.contains((' ' + brands_sim['Strip 13'][L] + ' '),
                                                                     case=False, regex=False)]
    i = 0
    if len(temp15) > 0:
        while i < len(temp15):
            common_company_names3['names'][a] = [brands_sim['Strip 13'][L] + '(name index:' + str(L) + ')']
            brands_sim['Strip 13'][L] = brands_sim['w/o_The3'][L]  # reset Strip 1 company names to not be common words
            common_company_names3['OG'][a] = brands_sim['affiliate'][L]
            i = i+1
            a = a+1
    L = L+1
common_company_names3 = common_company_names3.dropna()


brands_sim = brands_sim.rename(columns={'Strip 12': 'Strip 1'})
# want to put it all together now with companies, so we will have their brands with their parent companies and search
# for both
merge_companies = pd.merge(companies, brands_sim, on="Strip 1", how="outer")  # outer keeps everything, left keeps just
# the ones that have a match to left frame

# get a dataframe that is easier to look at
merge_companies_simp = merge_companies.copy(deep=True)

del merge_companies_simp['first1']
del merge_companies_simp['last1']
del merge_companies_simp['first2']
del merge_companies_simp['last2']
del merge_companies_simp['w/o_The']
del merge_companies_simp['"The"_Check']
del merge_companies_simp['"The"_Check_rem']
del merge_companies_simp['no punctuation']

del merge_companies_simp['first12']
del merge_companies_simp['last12']
del merge_companies_simp['first22']
del merge_companies_simp['last22']
del merge_companies_simp['w/o_The2']
del merge_companies_simp['"The"_Check2']
del merge_companies_simp['"The"_Check_rem2']
del merge_companies_simp['no punctuation2']

del merge_companies_simp['first13']
del merge_companies_simp['last13']
del merge_companies_simp['first23']
del merge_companies_simp['last23']
del merge_companies_simp['w/o_The3']
del merge_companies_simp['"The"_Check3']
del merge_companies_simp['"The"_Check_rem3']
del merge_companies_simp['no punctuation3']


# ToDo: why is united not on the list of public companies from Ari?

# SOLUTION: add list of common companies to list manually to affiliates file
# added uber, amazon, mcdonald, disney, shell, peloton, coke manually to
# changed "facebook INC" to META in multinational_affiliates, added META, Instagram, Whatsapp, facebook
# added most car brands

# publicly traded company - frontier (parent Indigo Partners) - labeled
# neuralink (publicly reported and can trade tokenized shares or tokenized stocks) - labeled

# bitcoin has a bunch of companies that deal with it - just label but don't connect to parent company
# multiple companies with bt in them - labeled them the biggest: BT GROUP PLC

# get rid of duplicates
# use the drop parameter to avoid the old index being added as a column:
merge_companies = merge_companies.drop_duplicates(subset=['Strip 13', 'Strip 1'],
                                                  keep='last').reset_index(drop=True)
# get rid of extra affiliates that didn't get matched with parent companies
merge_companies_no_extra = merge_companies.dropna(subset=['ISSUER_NAME'])
# save merged companies for checking
merge_companies_no_extra.to_csv(('merge_companies_' + str(date.today()) + '.csv'), index=False)

print("end all:", datetime.now())
