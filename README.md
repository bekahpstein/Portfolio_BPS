# Portfolio_BPS
## Learning Python through project based learning

This repository is sample code that I have written while learning Python through completing projects. 

The intent of the project was to identify and tag public companies and the board members from public companies mentioned in a set of news articles. The article_identification_1 cleans and simplifies the official names of publicly traded companies. The article_identification_2 searches the article names and article content for matches associated with companies, board members, and their associated ID numbers.

## article_identification_1
The article_identification_1 cleans and simplifies the official names of publicly traded companies by removing excess punctuation and any excess words which may not be used when a news article refers to a company. This simplification process is done in stages, and after, the names are checked against the 5000 most common English words. If the simplified name was in the 5000 most common English words, the name was deemed too common and, the simplification would be stepped back a stage.

**Using the folllowing steps, "The Coca-Cola Company" would be stripped to "Coca-Cola".**

"The" is removed from all company names:
```
for y, row in companies.iterrows():
    if row['"The"_Check'] == 'the':
        row['w/o_The'] = row['"The"_Check_rem']
    else:
        row['w/o_The'] = row['no punctuation']
```

Example word being removed - "Company" is removed from all company names:
```
for x, row in companies.iterrows():
    if row['last_word'] == 'company':
        row['Strip'] = row['first_word']
        # need to strip extra spaces off some company names
        row['Strip'] = row['Strip'].strip()
        temp_count = common_words_str.str.contains(' ' + row['Strip'] + ' ', regex=False).sum()
        if temp_count > 0:
            # if the company names after stripping can be found in the common word list - move back one step
            row['Strip'] = row['w/o_The']
    else:
        row['Strip'] = row['w/o_The']
```

Brands, nicknames, and conglomerate companies undergo the same cleaning and processing, then these two lists were merged based on the official parent company names. This final list of parent companies, conglomerates, brands, and nicknames (along with the identifying information needed for tagging) was exported to a CSV. 

## article_identification_2
The article_identification_2 imports the CSV output file from article_identification_1 and the aricle information. The script uses Natural Language Processing to simplify the names and content of the articles to only nouns and adjectives, limiting the words to be searched and limiting false tags. 

**Using NLP:**
```
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
```
    
**The script searches the article names and article content for matches associated with the company name, brands, nicknames, and conglomerate companies.** If "Coke" was used in an article, "The Coca-Cola Company" would be tagged along with the associated ID.

```
k = 0
while k < len(companies):
    temp1 = headlines.loc[headlines['nouns'].str.contains((' ' + companies['Strip'][k] + ' '), case=False,
                                                          regex=False)]
    i = 0
    if len(temp1) > 0:
        while i < len(temp1):
            if any(companies['Strip'][k] in sub for sub in headlines['Company Names (tag)'][temp1.index[i]]):
                # already in list, so do nothing
                nothing = 'nothing'
            else:
                headlines['Company Names (tag)'][temp1.index[i]] = headlines['Company Names (tag)'][temp1.index[i]] + \
                                                                   [companies['ISSUER_NAME'][k] + '(' +
                                                                    companies['Strip'][k] + ')']
                headlines['Company ISIN'][temp1.index[i]] = (headlines['Company ISIN'][temp1.index[i]] +
                                                             [companies['ISSUER_ISIN'][k]])
            i = i+1
    k = k+1
```

If a match is found, a tag is added to a list associated with that article including the full name, what was identified in the article, and the associated ID number. The same process was completed for board member's full names and associated individual ID numbers. The data frame is then exported and saved as a CSV.
