import pandas as pd

file = "data.csv"

df = pd.DataFrame({"netid": ["ap6178"], "password": ["FakePassword"], "booking-time": ["5:30pm - 6:30pm"]})
df.to_csv(file)