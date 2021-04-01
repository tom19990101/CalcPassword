import json, requests,time


def isChar(c):
    return c.isupper() or c.islower()

def callBitcoinByRpc(method, params=[]):
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": "minebet-{0}".format(time.time()),
        "method": method,
        "params": params
    })
    return requests.post("http://127.0.0.1:18332", auth=("rpcuser", "rpcpassword"), data=payload).json()


def main():
    s = list("abc+d")
    print ("".join(s))
    for i in range(len(s)):
        if not isChar(s[i]):
            continue;
        
        s = list("".join(s).lower())
        s[i] = s[i].upper()
        print ("".join(s))
        sub(s, i)

def sub(seeds, index):
    
    for i in range(0,index):
        if not isChar(seeds[i]):
            continue;

        s = list("".join(seeds[0:index]).lower() + "".join(seeds[index:]))
        s[i] = s[i].upper()
        print("".join(s))
        sub(s, i)

# main()

try:
    password = "aBc"
    result = callBitcoinByRpc('walletpassphrase', [password, 10])['error']
    if result is None:
        print(password)
        raise Exception("Sucess")
except BaseException as be:
    print(be)


