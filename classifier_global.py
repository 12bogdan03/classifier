import numpy as np
import pandas as pd
import pickle

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn import metrics

from lemmatization import lemmatize_text


def show_top10(classifier, vectorizer, categories):
    feature_names = np.asarray(vectorizer.get_feature_names())
    for i, category in enumerate(categories):
        top10 = np.argsort(classifier.coef_[i])[-10:]
        print("%s: %s" % (category, " ".join(feature_names[top10])))


#  Dataframe news
news_df = pd.read_csv('news.csv')
news_df.drop_duplicates()
news_df = news_df[pd.notnull(news_df['text'])]
news_df['topic'] = 'новини'
news_df['text_processed'] = news_df['text'].apply(lemmatize_text)
news_df = news_df[news_df.topic != 'АТО']

#  Dataframe articles 1
articles_df1 = pd.read_csv('nauka-online.csv')
articles_df1.drop_duplicates()
articles_df1 = articles_df1[pd.notnull(articles_df1['text'])]
articles_df1['topic'] = 'наукові статті'
articles_df1['text_processed'] = articles_df1['text'].apply(lemmatize_text)

#  Dataframe articles 2
articles_df2 = pd.read_csv('il-journal.csv', sep=';')
articles_df2.drop_duplicates()
articles_df2 = articles_df2[pd.notnull(articles_df2['text'])]
articles_df2['topic'] = 'наукові статті'
articles_df2['text_processed'] = articles_df2['text'].apply(lemmatize_text)

#  Dataframe reviews
reviews_df = pd.read_csv('litgazeta_reviews.csv')
reviews_df.drop_duplicates()
reviews_df = reviews_df[pd.notnull(reviews_df['text'])]
reviews_df['topic'] = 'рецензії'
reviews_df['text_processed'] = reviews_df['text'].apply(lemmatize_text)

#  Dataframe interviews
interviews_df = pd.read_csv('litgazeta_interviews.csv')
interviews_df.drop_duplicates()
interviews_df = interviews_df[pd.notnull(interviews_df['text'])]
interviews_df['topic'] = "інтерв'ю"
interviews_df['text_processed'] = interviews_df['text'].apply(lemmatize_text)

#  Dataframe Bible
bible_df = pd.read_csv('wordproject.csv')
bible_df.drop_duplicates()
bible_df = bible_df[pd.notnull(bible_df['text'])]
bible_df['topic'] = "біблійні тексти"
bible_df['text_processed'] = bible_df['text'].apply(lemmatize_text)

#  Dataframe Poetry
poetry_df = pd.read_csv('onlyart.csv')
poetry_df.drop_duplicates()
poetry_df = poetry_df[pd.notnull(poetry_df['text'])]
poetry_df['topic'] = "поезія"
poetry_df['text_processed'] = poetry_df['text'].apply(lemmatize_text)
counts = poetry_df['author'].value_counts()
poetry_df = poetry_df[~poetry_df['author'].isin(counts[counts < 10].index)]

df = pd.concat([
    news_df[['text_processed', 'topic']],
    articles_df1[['text_processed', 'topic']],
    articles_df2[['text_processed', 'topic']],
    reviews_df[['text_processed', 'topic']],
    interviews_df[['text_processed', 'topic']],
    bible_df[['text_processed', 'topic']],
    poetry_df[['text_processed', 'topic']],
], axis=0, ignore_index=True)

X_train, X_test, y_train, y_test = train_test_split(df['text_processed'],
                                                    df['topic'],
                                                    random_state=42)

vect = TfidfVectorizer()
X_train_transformed = vect.fit_transform(X_train)
X_test_transformed = vect.transform(X_test)

model = LinearSVC()
model.fit(X_train_transformed, y_train)
predictions = model.predict(X_test_transformed)

if __name__ == '__main__':
    print(metrics.classification_report(y_test, predictions))

    print("COUNTS:")
    print(df.groupby('topic').count())

    # cross_val = cross_val_score(model, X_test_transformed, y_test, cv=5)
    # print("Accuracy: %0.2f (+/- %0.2f)" % (cross_val.mean(), cross_val.std() * 2))
    print('CLASSES: ', model.classes_)
    #
    print('TOP FEATURES:')
    show_top10(model, vect, model.classes_)

    for input, prediction, label in zip(X_test, predictions, y_test):
        if prediction != label:
            print(input, 'has been classified as ', prediction, 'and should be ', label, '****\n****')

    pickle.dump(model, open('model_global.pickle', 'wb'))
    pickle.dump(vect, open('vectorizer_global.pickle', 'wb'))
