import time, pickle

NETID = "ap6178"

file = "cookies_{}}.pkl".format(NETID)
cookies = pickle.load(open(file, "rb"))
expiry = cookies[1]["expiry"]

print(time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.localtime(cookies[1]["expiry"])))