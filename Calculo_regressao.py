"Machine learn - regressão linear"
import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score

diabete_x, diabete_y = datasets.load_diabetes(return_X_y=True)

diabete_x = diabete_x[:, np.newaxis, 2]

diabete_x_train = diabete_x[:-20]
diabete_x_test = diabete_x[-20:]

diabete_y_train = diabete_y[:-20]
diabete_y_test = diabete_y[-20:]

regr = linear_model.LinearRegression()

regr.fit(diabete_x_train, diabete_y_train)

diabete_y_pred = regr.predict(diabete_x_test)

print('Coefficients: \n', regr.coef_)
print('Mean squared error: %.2f'
      % mean_squared_error(diabete_y_test, diabete_y_pred))
print('Coefficient of determination: %.2f'
      % r2_score(diabete_y_test, diabete_y_pred))

plt.scatter(diabete_x_test, diabete_y_test,  color='black')
plt.plot(diabete_x_test, diabete_y_pred, color='blue', linewidth=3)

plt.xticks(())
plt.yticks(())
plt.show()
