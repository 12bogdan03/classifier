import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn import metrics
import pickle

from lemmatization import lemmatize_text


def show_top10(classifier, vectorizer, categories):
    feature_names = np.asarray(vectorizer.get_feature_names())
    for i, category in enumerate(categories):
        top10 = np.argsort(classifier.coef_[i])[-10:]
        print("%s: %s" % (category, " ".join(feature_names[top10])))


#  Dataframe
df = pd.read_csv('onlyart.csv')
df.drop_duplicates()
df = df[pd.notnull(df['text'])]
counts = df['author'].value_counts()

df = df[~df['author'].isin(counts[counts < 10].index)]

print(df['author'].value_counts())
print(len(df['author'].value_counts()))

df['text_processed'] = df['text'].apply(lemmatize_text)
X_train, X_test, y_train, y_test = train_test_split(df['text_processed'],
                                                    df['author'],
                                                    random_state=42)

vect = TfidfVectorizer()
X_train_transformed = vect.fit_transform(X_train)
X_test_transformed = vect.transform(X_test)

model = LinearSVC()
model.fit(X_train_transformed, y_train)
predictions = model.predict(X_test_transformed)

if __name__ == '__main__':
    print(metrics.classification_report(y_test, predictions))

    # cross_val = cross_val_score(model, X_test_transformed, y_test, cv=5)
    # print("Accuracy: %0.2f (+/- %0.2f)" % (cross_val.mean(), cross_val.std() * 2))
    print('CLASSES: ', model.classes_)
    #
    print('TOP FEATURES:')
    show_top10(model, vect, model.classes_)

    for input, prediction, label in zip(X_test, predictions, y_test):
        if prediction != label:
            print(input, 'has been classified as ', prediction, 'and should be ', label, '****\n****')

    pickle.dump(model, open('model_poetry.pickle', 'wb'))
    pickle.dump(vect, open('vectorizer_poetry.pickle', 'wb'))
