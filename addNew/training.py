import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
import pickle

data=pd.read_csv(r'C:\Users\piyus\Desktop\Models\test1\Sign-Language-Translator\Sign-Language-Translator\Gesture.csv')
X=data.iloc[:,:-1].values
Y=data.iloc[:,-1].values

X_train,X_test,Y_train,Y_test=train_test_split(X,Y,test_size=0.25)

classifier=KNeighborsClassifier(n_neighbors=5)
classifier.fit(X_train,Y_train)

print(accuracy_score(Y_test,classifier.predict(X_test)))
model=open('model.pkl','wb')
pickle.dump(classifier,model)
model.close()