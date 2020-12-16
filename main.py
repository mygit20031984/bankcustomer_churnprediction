## REQUIRED LIBRARIES
# For data wrangling
import inline
import numpy as np
import pandas as pd

# For visualization
import matplotlib.pyplot as plt
import seaborn as sns
pd.options.display.max_rows = None
pd.options.display.max_columns = None

# Read the data frame
df = pd.read_csv('input/Churn_Modelling.csv', delimiter=',')
print(df.shape)
# Check columns list and missing values
#print(df.isnull().sum())
# Get unique count for each variable
#print(df.nunique())
# Drop the columns as explained above
df = df.drop(["RowNumber", "CustomerId", "Surname"], axis = 1)
#print(df.head())
# Check variable data types
#print(df.dtypes)

##############################################################################
#Exploratory Data Analysis
# labels = 'Exited', 'Retained'
# sizes = [df.Exited[df['Exited']==1].count(), df.Exited[df['Exited']==0].count()]
# explode = (0, 0.1)
# fig1, ax1 = plt.subplots(figsize=(10, 8))
# ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
# ax1.axis('equal')
# plt.title("Proportion of customer churned and retained", size = 20)
# plt.show()
##############################################################################
# # We first review the 'Status' relation with categorical variables
# fig, axarr = plt.subplots(2, 2, figsize=(20, 12))
# sns.countplot(x='Geography', hue='Exited', data=df, ax=axarr[0][0])
# sns.countplot(x='Gender', hue='Exited', data=df, ax=axarr[0][1])
# sns.countplot(x='HasCrCard', hue='Exited', data=df, ax=axarr[1][0])
# sns.countplot(x='IsActiveMember', hue='Exited', data=df, ax=axarr[1][1])
# plt.show()
##############################################################################
# Relations based on the continuous data attributes
# fig, axarr = plt.subplots(3, 2, figsize=(20, 12))
# sns.boxplot(y='CreditScore', x='Exited', hue='Exited', data=df, ax=axarr[0][0])
# sns.boxplot(y='Age', x='Exited', hue='Exited', data=df, ax=axarr[0][1])
# sns.boxplot(y='Tenure', x='Exited', hue='Exited', data=df, ax=axarr[1][0])
# sns.boxplot(y='Balance', x='Exited', hue='Exited', data=df, ax=axarr[1][1])
# sns.boxplot(y='NumOfProducts', x='Exited', hue='Exited', data=df, ax=axarr[2][0])
# sns.boxplot(y='EstimatedSalary', x='Exited', hue='Exited', data=df, ax=axarr[2][1])
##############################################################################
# Split Train, test data
df_train = df.sample(frac=0.8,random_state=200)
df_test = df.drop(df_train.index)
print(len(df_train))
print(len(df_test))
# ##############################################################################
df_train['BalanceSalaryRatio'] = df_train.Balance/df_train.EstimatedSalary
#sns.boxplot(y='BalanceSalaryRatio',x = 'Exited', hue = 'Exited',data = df_train)
#plt.ylim(-1, 5)
################################################################################
# Given that tenure is a 'function' of age, we introduce a variable aiming to standardize tenure over age:
df_train['TenureByAge'] = df_train.Tenure/(df_train.Age)
# sns.boxplot(y='TenureByAge',x = 'Exited', hue = 'Exited',data = df_train)
# plt.ylim(-1, 1)
# plt.show()
################################################################################
#'''Lastly we introduce a variable to capture credit score given age to take into account credit behaviour visavis adult life :-)'''
df_train['CreditScoreGivenAge'] = df_train.CreditScore/(df_train.Age)
# Resulting Data Frame
continuous_vars = ['CreditScore',  'Age', 'Tenure', 'Balance','NumOfProducts', 'EstimatedSalary', 'BalanceSalaryRatio',
                   'TenureByAge','CreditScoreGivenAge']
cat_vars = ['HasCrCard', 'IsActiveMember','Geography', 'Gender']
df_train = df_train[['Exited'] + continuous_vars + cat_vars]
'''For the one hot variables, we change 0 to -1 so that the models can capture a negative relation 
where the attribute in inapplicable instead of 0'''
df_train.loc[df_train.HasCrCard == 0, 'HasCrCard'] = -1
df_train.loc[df_train.IsActiveMember == 0, 'IsActiveMember'] = -1
# One hot encode the categorical variables
lst = ['Geography', 'Gender']
remove = list()
for i in lst:
    if (df_train[i].dtype == np.str or df_train[i].dtype == np.object):
        for j in df_train[i].unique():
            df_train[i+'_'+j] = np.where(df_train[i] == j,1,-1)
        remove.append(i)
df_train = df_train.drop(remove, axis=1)
# minMax scaling the continuous variables
minVec = df_train[continuous_vars].min().copy()
maxVec = df_train[continuous_vars].max().copy()
df_train[continuous_vars] = (df_train[continuous_vars]-minVec)/(maxVec-minVec)
################################################################################
################################################################################
################################################################################
# Support functions
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV
from scipy.stats import uniform

# Fit models
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

# Scoring functions
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve

# Function to give best model score and parameters
def best_model(model):
    print(model.best_score_)
    print(model.best_params_)
    print(model.best_estimator_)
def get_auc_scores(y_actual, method,method2):
    auc_score = roc_auc_score(y_actual, method);
    fpr_df, tpr_df, _ = roc_curve(y_actual, method2);
    return (auc_score, fpr_df, tpr_df)
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
# # Fit primal logistic regression
# param_grid = {'C': [0.1,0.5,1,10,50,100], 'max_iter': [250], 'fit_intercept':[True],'intercept_scaling':[1],
#               'penalty':['l2'], 'tol':[0.00001,0.0001,0.000001]}
# log_primal_Grid = GridSearchCV(LogisticRegression(solver='lbfgs'),param_grid, cv=10, refit=True, verbose=0)
# log_primal_Grid.fit(df_train.loc[:, df_train.columns != 'Exited'],df_train.Exited)
# best_model(log_primal_Grid)
#
# # Fit logistic regression with degree 2 polynomial kernel
# param_grid = {'C': [0.1,10,50], 'max_iter': [300,500], 'fit_intercept':[True],'intercept_scaling':[1],'penalty':['l2'],
#               'tol':[0.0001,0.000001]}
# poly2 = PolynomialFeatures(degree=2)
# df_train_pol2 = poly2.fit_transform(df_train.loc[:, df_train.columns != 'Exited'])
# log_pol2_Grid = GridSearchCV(LogisticRegression(solver = 'liblinear'),param_grid, cv=5, refit=True, verbose=0)
# log_pol2_Grid.fit(df_train_pol2,df_train.Exited)
# best_model(log_pol2_Grid)
# Fit SVM with RBF Kernel
# param_grid = {'C': [0.5,100,150], 'gamma': [0.1,0.01,0.001],'probability':[True],'kernel': ['rbf']}
# SVM_grid = GridSearchCV(SVC(), param_grid, cv=3, refit=True, verbose=0)
# SVM_grid.fit(df_train.loc[:, df_train.columns != 'Exited'],df_train.Exited)
# best_model(SVM_grid)
# Fit SVM with pol kernel
# param_grid = {'C': [0.5,1,10,50,100], 'gamma': [0.1,0.01,0.001],'probability':[True],'kernel': ['poly'],'degree':[2,3] }
# SVM_grid = GridSearchCV(SVC(), param_grid, cv=3, refit=True, verbose=0)
# SVM_grid.fit(df_train.loc[:, df_train.columns != 'Exited'],df_train.Exited)
# best_model(SVM_grid)
# Fit random forest classifier
# param_grid = {'max_depth': [3, 5, 6, 7, 8], 'max_features': [2,4,6,7,8,9],'n_estimators':[50,100],'min_samples_split': [3, 5, 6, 7]}
# RanFor_grid = GridSearchCV(RandomForestClassifier(), param_grid, cv=5, refit=True, verbose=0)
# RanFor_grid.fit(df_train.loc[:, df_train.columns != 'Exited'],df_train.Exited)
# best_model(RanFor_grid)
# Fit Extreme Gradient boosting classifier
# param_grid = {'max_depth': [5,6,7,8], 'gamma': [0.01,0.001,0.001],'min_child_weight':[1,5,10], 'learning_rate': [0.05,0.1, 0.2, 0.3], 'n_estimators':[5,10,20,100]}
# xgb_grid = GridSearchCV(XGBClassifier(), param_grid, cv=5, refit=True, verbose=0)
# xgb_grid.fit(df_train.loc[:, df_train.columns != 'Exited'],df_train.Exited)
# best_model(xgb_grid)
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#Fit Best Model
# Fit logistic regression with degree 2 polynomial kernel
# param_grid = {'C': [0.1,10,50], 'max_iter': [300,500], 'fit_intercept':[True],'intercept_scaling':[1],'penalty':['l2'],
#               'tol':[0.0001,0.000001]}
# poly2 = PolynomialFeatures(degree=2)
# df_train_pol2 = poly2.fit_transform(df_train.loc[:, df_train.columns != 'Exited'])
# log_pol2_Grid = GridSearchCV(LogisticRegression(solver = 'liblinear'),param_grid, cv=5, refit=True, verbose=0)
# log_pol2_Grid.fit(df_train_pol2,df_train.Exited)
# best_model(log_pol2_Grid)

# Fit logistic regression with pol 2 kernel
poly2 = PolynomialFeatures(degree=2)
df_train_pol2 = poly2.fit_transform(df_train.loc[:, df_train.columns != 'Exited'])
log_pol2 = LogisticRegression(C=10, class_weight=None, dual=False, fit_intercept=True,intercept_scaling=1, max_iter=300, multi_class='auto', n_jobs=None,
                              penalty='l2', random_state=None, solver='liblinear',tol=0.0001, verbose=0, warm_start=False)
log_pol2.fit(df_train_pol2,df_train.Exited)
