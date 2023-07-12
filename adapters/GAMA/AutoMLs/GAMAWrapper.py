from sklearn.base import BaseEstimator, ClassifierMixin

class GAMAWrapper(BaseEstimator, ClassifierMixin):
    def __init__(self, model):
        self.model = model

    def fit(
        self,
        X=None,
        y=None,):
        self._model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)

    def predict_proba(self, X):
        return self.model.predict_proba(X).tolist()
