from collections import Counter
from nltk.tag import PerceptronTagger
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

df = pd.read_csv('tagged.csv', header=None)
X_train, X_test, y_train, y_test = train_test_split(df[0],
                                                    df[1],
                                                    random_state=42)

tagger = PerceptronTagger(load=False)
tagger.train([list(zip(X_train, y_train))])

if __name__ == '__main__':
    predictions = [i[1] for i in tagger.tag(X_test)]
    print(Counter(tagger.tag(X_test)).most_common(30))
    print(classification_report(y_test, predictions))
