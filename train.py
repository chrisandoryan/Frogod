from sklearn import svm
import pandas as pd  
import numpy as np  
import matplotlib.pyplot as plt
import seaborn as sns
from mlxtend.plotting import plot_decision_regions

from sklearn.model_selection import train_test_split  
from sklearn.model_selection import cross_val_score
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV

from sklearn.metrics import classification_report, confusion_matrix  
from sklearn.metrics import accuracy_score

from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import RobustScaler
from sklearn.feature_extraction.text import CountVectorizer


from sklearn.naive_bayes import GaussianNB


from sklearn.externals import joblib

"""  Parameter Tuning  """
# gamma = 100
kernel = "rbf"
# c = 10
"""                    """

DATASET_LOCATION = "./data_temp/AGG.csv"
UNUSED_COLS = [
    "payload",
    "query",
    "req_method",
    "u_agent",
    "category",
    "timestamp_x",
    "timestamp_y",
]

def svc_param_selection(X, y, nfolds):
    Cs = [0.001, 0.01, 0.1, 1, 10]
    gammas = [0.001, 0.01, 0.1, 1]
    param_grid = {'C': Cs, 'gamma' : gammas}
    grid_search = GridSearchCV(svm.SVC(kernel='rbf'), param_grid, cv=nfolds)
    grid_search.fit(X, y)
    grid_search.best_params_
    return grid_search.best_params_

def drop_unused_columns(data):
    for i in UNUSED_COLS:
        data.drop(i, axis=1, inplace=True)

def train_model():
    data = pd.read_csv(DATASET_LOCATION)
    data.drop_duplicates(subset=["payload","query"], inplace=True)
    print(data.shape)
    # print(data.head())
    
    # remove unused data column
    drop_unused_columns(data)


    print(data.groupby('class').size())
    sns.heatmap(data.corr() , annot=True)
    plt.show()
    # data.drop('uagent', axis=1, inplace=True)
    # data.drop('reqmethod', axis=1, inplace=True)
    # data.drop('payload', axis=1, inplace=True)
    # data.drop('class', axis=1, inplace=True)
    # data.drop('centrality', axis=1, inplace=True)
    # data.drop('length', axis=1, inplace=True)

    print("DATAHEAD")
    print(data.shape)
    print(data.head())

    # input()
    # input()

    # data separation
    X = data.drop('class', axis=1)  
    # X_nonumer = X.select_dtypes(include=[object])
    print("XHEAD")
    print(X.shape)
    print(X.head())

    y = data['class']

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
    # input("Holding...")
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

    X_train, X_test, y_train, y_test = train_test_split(X_t, y, random_state=0, test_size = 0.30, stratify=y_t)

    bp = svc_param_selection(X_train, y_train, 10)

    # input("Best params selected..")
    print("Best kernel param: ")
    print(bp)

    svclassifier = SVC(kernel=kernel, gamma=bp['gamma'], C=bp['C'], cache_size=7000, verbose=True)  
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
    # input(acc)

    # input("Holding...")

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
    print("Model columns: ")
    print(model_columns)

    joblib.dump(svclassifier, './models/model.pkl')

if __name__ == "__main__":
    train_model()