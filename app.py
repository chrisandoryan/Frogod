import falcon
from sklearn.externals import joblib
import pandas as pd
from middleware import JSONValidator
import grpc, cvss_pb2, cvss_pb2_grpc

class Predictor():
     def on_post(self, req, resp):
          req = req.context["request"]

          # query_df = pd.DataFrame(req)
          # query = pd.get_dummies(query_df)
     
          # for col in model_columns:
          #      if col not in query.columns:
          #           query[col] = 0

          prediction = []#model.predict(query)

          cvss_calc = stub.getVector(cvss_pb2.Event(ip=req["ip"], url=req["url"], vul=cvss_pb2.Event.SQL))

          resp.context["response"] = {k.camelcase_name:v for k,v in cvss_calc.ListFields()}
          resp.context["response"]["prediction"] = list(prediction)
          resp.status = falcon.HTTP_200


chan = grpc.insecure_channel('localhost:5000')
stub = cvss_pb2_grpc.CVSSSvcStub(chan) 

model = joblib.load('model.pkl')
model_columns = joblib.load('model_columns.pkl')
app = falcon.API(middleware=[JSONValidator()])
app.add_route('/predict', Predictor())