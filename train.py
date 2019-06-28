from sklearn import svm
import pandas as pd  
import numpy as np  
import matplotlib.pyplot as plt
from mlxtend.plotting import plot_decision_regions

from sklearn.model_selection import train_test_split  
from sklearn.model_selection import cross_val_score
from sklearn.svm import SVC  

from sklearn.metrics import classification_report, confusion_matrix  
from sklearn.metrics import accuracy_score

from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import RobustScaler
from sklearn.feature_extraction.text import CountVectorizer

from sklearn.naive_bayes import GaussianNB


from sklearn.externals import joblib

"""  Parameter Tuning  """
gamma = 100
kernel = "rbf"
c = 10
"""                    """

def train_model():
    data = pd.read_csv('./samples/GET_new.csv')
    # print(data.shape)
    # print(data.head())

    # remove unused data column
    data.drop('uagent', axis=1, inplace=True)
    data.drop('reqmethod', axis=1, inplace=True)
    data.drop('payload', axis=1, inplace=True)
    data.drop('class', axis=1, inplace=True)
    # data.drop('centrality', axis=1, inplace=True)
    # data.drop('length', axis=1, inplace=True)

    # data separation
    X = data.drop('label', axis=1)  
    X = X.select_dtypes(include=[object])
    print(X.head())

    y = data['label']

    count_vec = CountVectorizer()
    count_occurs = count_vec.fit_transform(X['token'])
    # print(count_vec.get_feature_names())
    # print(count_occurs.toarray())

    X['token'] = count_occurs.toarray()

    # fit and transform
    label_encoder = LabelEncoder()
    X_t = X.apply(label_encoder.fit_transform)
    y_t = label_encoder.fit(y).transform(y)

    scaler = RobustScaler()
    X_t = scaler.fit_transform(X_t)

    print(X_t)
    input("Holding...")
    # count_occur_df = pd.DataFrame(
    # (count, word) for word, count in
    #  zip(count_occurs.toarray().tolist()[0], 
    # count_vec.get_feature_names()))
    # count_occur_df.columns = ['Word', 'Count']
    # count_occur_df.sort_values('Count', ascending=False, inplace=True)
    # count_occur_df.head()

    print("Features: ")
    print(X_t)
    print("Labels: ")
    print(y_t)

    # onehot_encoder = OneHotEncoder(categories='auto',sparse=False)
    # onehot_encoder.fit(X_t)
    # onehotlabels = label_encoder.transform(X_t).toarray()
    # print(onehotlabels.shape)

    X_train, X_test, y_train, y_test = train_test_split(X_t, y, test_size = 0.30)


    svclassifier = SVC(kernel=kernel, gamma=gamma, C=c, cache_size=7000, verbose=True)  
    svclassifier.fit(X_train, y_train)

    y_pred = svclassifier.predict(X_test)

    conf = confusion_matrix(y_test,y_pred)
    rept = classification_report(y_test,y_pred)
    acc = accuracy_score(y_pred, y_test)
    
    print("Training using SVM Classifier...")

    print(conf)
    print(rept)
    print(acc)


    bayesclassifier = GaussianNB()
    bayesclassifier.fit(X_train, y_train)

    y_pred = bayesclassifier.predict(X_test)

    conf = confusion_matrix(y_test,y_pred)
    rept = classification_report(y_test,y_pred)
    acc = accuracy_score(y_pred, y_test)
    
    print("Training using Naive Bayes...")

    print(conf)
    print(rept)
    print(acc)

    input("Holding...")

    scores = cross_val_score(svclassifier, X_t, y_t, cv=10)
    print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

    # plot_decision_regions(
    #     X=X_t, 
    #     y=y_t, clf=svclassifier, 
    #     legend=2,
    #     feature_index=[0,2],
    # )

    # plt.xlabel(X_t.columns[0], size=14)
    # plt.ylabel(X_t.columns[1], size=14)
    # plt.title('SVM Decision Region Boundary', size=16)
    # plt.show()

    # plt.imshow(conf, cmap='binary', interpolation='None')

    model_columns = list(X.columns)
    print(model_columns)

    joblib.dump(svclassifier, './models/model.pkl')

if __name__ == "__main__":
    train_model()