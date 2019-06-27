from sklearn import svm
import pandas as pd  
import numpy as np  
import matplotlib.pyplot as plt
from mlxtend.plotting import plot_decision_regions

from sklearn.model_selection import train_test_split  
from sklearn.svm import SVC  
from sklearn.metrics import classification_report, confusion_matrix  
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import accuracy_score
from sklearn.externals import joblib

def train_model():
    # TODO: determine feature structures. then train the model.
    data = pd.read_csv('./samples/GET_new.csv')
    print(data.shape)
    print(data.head())

    # remove unused data column
    data.drop('uagent', axis=1, inplace=True)
    data.drop('reqmethod', axis=1, inplace=True)
    data.drop('payload', axis=1, inplace=True)
    data.drop('class', axis=1, inplace=True)

    # data separation
    X = data.drop('label', axis=1)  
    X = X.select_dtypes(include=[object])
    y = data['label']

    # fit and transform
    label_encoder = LabelEncoder()
    X_t = X.apply(label_encoder.fit_transform)
    y_t = label_encoder.fit(y).transform(y)

    # print(X_t)
    # input()

    # onehot_encoder = OneHotEncoder(categories='auto',sparse=False)
    # onehot_encoder.fit(X_t)
    # onehotlabels = label_encoder.transform(X_t).toarray()
    # print(onehotlabels.shape)

    X_train, X_test, y_train, y_test = train_test_split(X_t, y, test_size = 0.40)

    svclassifier = SVC(kernel='linear')  
    svclassifier.fit(X_train, y_train)  

    y_pred = svclassifier.predict(X_test)

    conf = confusion_matrix(y_test,y_pred)
    rept = classification_report(y_test,y_pred)
    acc = accuracy_score(y_pred, y_test)

    print(conf)
    print(rept)
    print(acc)

    # plot_decision_regions(
    #     X=X_t.values, 
    #     y=y_t, clf=svclassifier, 
    #     legend=2,
    #     feature_index=[0,1],
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