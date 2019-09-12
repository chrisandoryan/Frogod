import falcon
from sklearn.externals import joblib
import pandas as pd
from middleware import JSONValidator

class Predictor():
     def on_post(self, req, resp):
          req = req.context["request"]

          query_df = pd.DataFrame(req)
          query = pd.get_dummies(query_df)
     
          for col in model_columns:
               if col not in query.columns:
                    query[col] = 0

          prediction = model.predict(query)

          resp.context["response"] = {'prediction': list(prediction)}
          resp.status = falcon.HTTP_200


model = joblib.load('model.pkl')
model_columns = joblib.load('model_columns.pkl')
app = falcon.API(middleware=[JSONValidator()])
app.add_route('/predict', Predictor())