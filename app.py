import os
#os.remove("model1.h5")
import numpy as np
from flask import Flask, request, jsonify, render_template
import pickle
import tensorflow as tf
from tensorflow.keras.preprocessing.text import one_hot
import re
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pandas as pd
from urllib.parse import urlparse, urlencode
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dense
import whois
import ipaddress
import csv
from datetime import datetime
import requests
import ssl, socket

#PORT = int(os.environ.get('PORT'), 4567)

df = pd.read_csv('finaldata.csv')
x= df['url']
y = df['label']

voc_size = 10000
messages = x.copy()

corpus = []


for i in range(0, len(messages)):
    review = re.sub('[^a-zA-Z]',' ',urlparse(messages[i]).netloc)
    review = review.lower()
    review = review.split()
    review=' '.join(review)
    corpus.append(review)

onehot_repr=[one_hot(words,voc_size)for words in corpus]
sent_length = 50
embedded_docs= pad_sequences(onehot_repr,padding='pre',maxlen=sent_length)

embedded_docs = np.array(embedded_docs)

#x_final = np.array(embedded_docs)
x_final = embedded_docs
y_final  = np.array(y)
from sklearn.model_selection import train_test_split
x_train,x_test,y_train,y_test = train_test_split(x_final,y_final,test_size=0.20)


#make the model and train it
embedding_vector_features=100
model = Sequential()
model.add(Embedding(voc_size,embedding_vector_features,input_length=sent_length))
model.add(LSTM(100))
model.add(Dense(1,activation='sigmoid'))
model.compile(loss='binary_crossentropy',optimizer='adam',metrics=['accuracy'])


model.fit(x_train,y_train,validation_data=(x_test,y_test),epochs=2,batch_size=64)

y_pred1=model.predict(x_test) 
classes_y1=np.round(y_pred1).astype(int)
from sklearn.metrics import confusion_matrix
confusion_n = confusion_matrix(y_test,classes_y1)
from sklearn.metrics import accuracy_score
print(accuracy_score(y_test, classes_y1))
model.save("model1.h5")

def domaincreatedate(url):
    try:
        whois_info = whois.whois(url)
        cd = whois_info.get('creation_date')
        if whois_info.get('domain_name') == None:
            cd = 'No domain information for this URL'
        return cd
    except:
        return 'No informations about Domain creation date'
    
def domainexpiredate(url):
    try:
        whois_info = whois.whois(url)
        cd = whois_info.get('expiration_date')
        if whois_info.get('domain_name') == None:
            cd = 'No domain information for this URL'
        return cd
    except:
        return 'No informations about Domain expiration date'

def ageofdomain1(url):
    try:
        whois_info = whois.whois(url)
        ex = whois_info.get('expiration_date')
        cd = whois_info.get('creation_date')
        expiration_date = ex[0]
        creation_date = cd[0]
        days = abs((expiration_date - creation_date).days)
        if whois_info.get('domain_name')== None:
            days = 'No Domain informations about this URL'
        return days
    except :
        pass
    try:
        whois_info = whois.whois(url)
        ex = whois_info.get('expiration_date')
        cd = whois_info.get('creation_date')
        expiration_date = ex
        creation_date = cd
        days = abs((expiration_date - creation_date).days)
        if whois_info.get('domain_name')== None:
            days = 'No Domain informations about this URL'
        return days
    except:
        pass
    
    try:
        whois_info = whois.whois(url)
        ex = whois_info.get('expiration_date')
        cd = whois_info.get('creation_date')
        expiration_date = ex
        creation_date = cd[0]
        days = abs((expiration_date - creation_date).days)
        if whois_info.get('domain_name')== None:
            days = 'No Domain informations about this URL'
        return days
    except:
        pass
    try:
        whois_info = whois.whois(url)
        ex = whois_info.get('expiration_date')
        cd = whois_info.get('creation_date')
        expiration_date = ex[0]
        creation_date = cd
        days = abs((expiration_date - creation_date).days)
        if whois_info.get('domain_name')== None:
            days = 'No Domain informations about this URL'
        return days
    except:
        return 'No Domain information about this URL'
def havingIP1(url):
  try:
    ipaddress.ip_address(url)
    ip = 1
    msg= 'ip is displayed'
  except:
    ip = 0
    msg= 'ip isnt displayed'
  return msg
def havingAtsign1(url):
    if "@" in url:
        at = 'No special character in URL'
    else:
        at = 'Special characters are in URL'
    return at
def getLength1(url):
  if len(url) < 54:
    length = 'Normal length URL'
  else:
    length = 'Suspicious length URL'
  return length
def getDepth1(url):
  s = urlparse(url).path.split('/')
  depth = 0
  for j in range(len(s)):
    if len(s[j]) != 0:
      depth = depth+1
  return depth
def redirection1(url):
    pos = url.rfind('//')
    if pos > 6:
        if pos > 7:
            return 'URL contains redirecting URL'
        else:
            return 'URL doesnt contain redirecting URL'
    else:
        return 'URL doesnt contain redirecting URL'
def httpDomain1(url):
  domain = urlparse(url).netloc
  if 'https' in domain:
    return 'defined certificate'
  else:
    return 'not defined certificate'
shortening_services = r"bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|" \
                      r"yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|" \
                      r"short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|" \
                      r"doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|db\.tt|" \
                      r"qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|q\.gs|is\.gd|" \
                      r"po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|x\.co|" \
                      r"prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|" \
                      r"tr\.im|link\.zip\.net"
def tinyURL1(url):
    match=re.search(shortening_services,url)
    if match:
        return 'url is using shortening service'
    else:
        return 'url is not using shortening service'
def prefixSuffix1(url):
    if '-' in urlparse(url).netloc:
        return 'special characters contain'
    else:
        return 'special character doesnt contain' 
def dnsrecord1(url):
    dns = 'DNS information can be found'
    try:
        domain_name = whois.whois(url)
        if domain_name.get('domain_name') == None:
            dns = 'doesnt contain DNS information'
    except:
        dns = 'could not find DNS information'
    return dns
def iframe1(response):
    if response == '':
        return 'doesnt show the response'
    else:
        if re.findall((r'[<iframe>|<frameBorder>]'), response.text):
            return 'doesnt contain iframe in response'
        else:
            return 'iframe is contained in response'
def forwading1(response):
    if response == '':
        return 1
    else:
        if len(response.history)<= 2:
            return 'does not redirect'
        else:
            return 'does redirect to other pages'
def mouseOver1(response):
    if response == '':
        return 1
    else:
        if re.findall("<script>.+onmouseover.+</script>", response.text):
            return 'onmouseover event found'
        else:
            return 'onmouseover event not found'

app = Flask(__name__)
model = tf.keras.models.load_model('model1.h5')
modelfeature = tf.keras.models.load_model('modelGRU.h5')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict',methods=['POST'])
def predict():
    
    voc_size = 10000
    corpus=[]
    classes_y=''
    status=''
    showmsg1=''
    a=''
    b=''
    urlstatus=''
    for i in request.form.values():
        
    #messages = [str(x) for x in request.form.values()]
        API_KEY = '791eb60b503f0d31540d9a84c3160c13844f4cb24fc3491ab3b03829a585b300'    
        messages = i
        messages = urlparse(messages).netloc
        if messages =='':
            status="Enter url in valid format Ex - ' https://www.example.com ' "
            a=1
        else:
            status="URL is in valid format:"
            a=2
        #reading the whitelist
        
        f=open("whitelist.txt","r")
        if messages in f.read():
            showmsg1 = "this is legitimate"
            b=1
        else:
            showmsg1 = "whitelist does not have any record!"
            b=2
            
        review = re.sub('[^a-zA-Z]',' ',messages)
        review = review.lower()
        review = review.split()
        review=' '.join(review)
        corpus.append(review)
        onehot_repr=[one_hot(words,voc_size)for words in corpus]
        print(onehot_repr)
        sent_length = 50
        embedded_docs= pad_sequences(onehot_repr,padding='pre',maxlen=sent_length)
        x_test = embedded_docs
        y_pred = model.predict(x_test)
        classes_y=np.round(y_pred).astype(int)
        
        if y_pred < 0.4:
            urlstatus = "Legitimate URL"
        elif 0.4 < y_pred < 0.6:
            urlstatus = "This can be a Phishing URL"
        else:
            urlstatus = "Phishing URL"
        
        
        # if status==1:
        #     if review == "":
        #         showmsg1 = "enter valid url format"
        #     else:
        #         classes_y=np.round(y_pred).astype(int)
        # else:
        #     showmsg1="something went wrong"
            
        createdDate = domaincreatedate(messages)
        domainAge = ageofdomain1(messages)
        expiredate = domainexpiredate(messages)
        havingip = havingIP1(messages)
        havingat2 = havingAtsign1(messages)
        urllength2 = getLength1(messages)
        urldepth2 = getDepth1(messages)
        urlredirection2 = redirection1(messages)
        urlhttps = httpDomain1(messages)
        urltiny = tinyURL1(messages)
        urlprefix = prefixSuffix1(messages)
        urldnsrecord = dnsrecord1(messages)
    
        try:
            response = requests.get(i)
        except:
            response = ''
        urliframe = iframe1(response)
        urlforward = forwading1(response)
        urlmouseover = mouseOver1(response)
        
        
        
        
        ###
        ##
        # feature based model loading
        
        header = ['url']
        data = [i]
        with open('test.csv','w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerow(data)
            f.close()
        
        df = pd.read_csv('test.csv')
        def havingIP(url):
          try:
            ipaddress.ip_address(url)
            ip = 1
          except:
            ip = 0
          return ip


        list=[]
        for i in df.url:
            ip = havingIP(i)
            list.append(ip)
        df['Have_IP']=list
        df.to_csv('test1.csv',index=False)
        #feature based detection
        
        def havingAtsign(url):
            if "@" in url:
                at = 1
            else:
                at = 0
            return at

        list=[]
        for i in df.url:
            at = havingAtsign(i)
            list.append(at)
        df['Have_At']=list
        df.to_csv('test1.csv',index=False)

        #checking length of url
        def getLength(url):
          if len(url) < 54:
            length = 0
          else:
            length = 1
          return length

        list = []
        for i in df.url:
            l = getLength(i)
            list.append(l)
        df['URL_Length']=list
        df.to_csv('test1.csv',index=False)

        #checking url depth
        def getDepth(url):
          s = urlparse(url).path.split('/')
          depth = 0
          for j in range(len(s)):
            if len(s[j]) != 0:
              depth = depth+1
          return depth

        list=[]
        for i in df.url:
            d= getDepth(i)
            list.append(d)
        df['URL_Depth']=list
        df.to_csv('test1.csv',index=False)

        #checking redirection information
        def redirection(url):
            pos = url.rfind('//')
            if pos > 6:
                if pos > 7:
                    return 1
                else:
                    return 0
            else:
                return 0

        list=[]
        for i in df.url:
            p = redirection(i)
            list.append(p)
        df['Redirection']=list
        df.to_csv('test1.csv',index=False)

        #checking https in domain
        def httpDomain(url):
          domain = urlparse(url).netloc
          if 'https' in domain:
            return 1
          else:
            return 0

        list=[]
        for i in df.url:
            d = httpDomain(i)
            list.append(d)
        df['https_Domain']=list
        df.to_csv('test1.csv',index=False)

        #checking shortening url status
        shortening_services = r"bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|" \
                              r"yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|" \
                              r"short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|" \
                              r"doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|db\.tt|" \
                              r"qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|q\.gs|is\.gd|" \
                              r"po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|x\.co|" \
                              r"prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|" \
                              r"tr\.im|link\.zip\.net"
        def tinyURL(url):
            match=re.search(shortening_services,url)
            if match:
                return 1
            else:
                return 0

        list=[]
        for i in df.url:
            t = tinyURL(i)
            list.append(t)
        df['TinyURL']=list
        df.to_csv('test1.csv',index=False)

        #checking - in prefix or suffix
        def prefixSuffix(url):
            if '-' in urlparse(url).netloc:
                return 1
            else:
                return 0

        list=[]
        for i in df.url:
            p = prefixSuffix(i)
            list.append(p)
        df['Prefix/Suffix']=list
        df.to_csv('test1.csv',index=False)

        #checking dns records
        def dnsrecord(url):
            dns = 0
            try:
                domain_name = whois.whois(url)
                if domain_name.get('domain_name') == None:
                    dns = 1
            except:
                dns =1
            return dns
                
        list=[]
        for i in df.url:
            dns = dnsrecord(i)
            list.append(dns)
        df['DNS_Record']=list
        df.to_csv('test1.csv',index=False)

        #calculating domain age
        def ageofdomain(url):
            try:
                whois_info = whois.whois(url)
                if whois_info.get('domain_name')== None:
                    days = 1
                ex = whois_info.get('expiration_date')
                cd = whois_info.get('creation_date')
                expiration_date = ex[0]
                creation_date = cd[0]
                days = abs((expiration_date - creation_date).days)
                if days > 360:
                    days = 0
                
                return days
            except :
                pass
            try:
                whois_info = whois.whois(url)
                if whois_info.get('domain_name')== None:
                    days = 1
                ex = whois_info.get('expiration_date')
                cd = whois_info.get('creation_date')
                expiration_date = ex
                creation_date = cd
                days = abs((expiration_date - creation_date).days)
                if days > 360:
                    days = 0
                
                return days
            except:
                pass
            
            try:
                whois_info = whois.whois(url)
                if whois_info.get('domain_name')== None:
                    days = 1
                ex = whois_info.get('expiration_date')
                cd = whois_info.get('creation_date')
                expiration_date = ex
                creation_date = cd[0]
                days = abs((expiration_date - creation_date).days)
                if days > 360:
                    days = 0
                
                return days
            except:
                pass
            try:
                whois_info = whois.whois(url)
                if whois_info.get('domain_name')== None:
                    days = 1
                ex = whois_info.get('expiration_date')
                cd = whois_info.get('creation_date')
                expiration_date = ex[0]
                creation_date = cd
                days = abs((expiration_date - creation_date).days)
                if days > 360:
                    days = 0
                
                return days
            except:
                return 1
        list=[]
        for i in df.url:
            dns = ageofdomain(i)
            list.append(dns)
        df['Domain_age']=list
        df.to_csv('test1.csv',index=False)

        #domain time until it expires
        def domaintime(url):
            try:
                whois_info = whois.whois(url)
                if whois_info.get('domain_name')== None:
                    day = 1
                ex = whois_info.get('expiration_date')
                expiration_date = ex[0] 
                nt = datetime.now()
                days = abs((expiration_date - nt).days)
                if days > 180:
                    day = 0
                else:
                    day = 1
                return day
            except:
                pass
            
            try:
                whois_info = whois.whois(url)
                if whois_info.get('domain_name')==None:
                    day = 1
                ex = whois_info.get('expiration_date')
                expiration_date = ex
                nt = datetime.now()
                days = abs((expiration_date - nt).days)
                if days > 180:
                    day = 0
                else:
                    day = 1
                return day
           
            except:
                return 1
            
        list=[]
        for i in df.url:
            dns = domaintime(i)
            list.append(dns)
        df['Domain_time']=list
        df.to_csv('test1.csv',index=False)

        #checking iframe in html code
        def iframe(response):
            if response == '':
                return 1
            else:
                if re.findall((r'[<iframe>|<frameBorder>]'), response.text):
                    return 0
                else:
                    return 1

        list=[]
        for i in df.url:
            try:
                response = requests.get(i)
            except:
                response = ''
            frame = iframe(response)
            list.append(frame)
        df['iFrame']=list
        df.to_csv('test1.csv',index=False)

        #checking mouse over
        def mouseOver(response):
            if response == '':
                return 1
            else:
                if re.findall("<script>.+onmouseover.+</script>", response.text):
                    return 1
                else:
                    return 0

        list=[]
        for i in df.url:
            try:
                response = requests.get(i)
            except:
                response = ''
            fake = mouseOver(response)
            list.append(fake)
        df['Mouse_Over'] = list
        df.to_csv('test1.csv',index=False)

        #checking website is forwarding or not
        def forwading(response):
            if response == '':
                return 1
            else:
                if len(response.history)<= 2:
                    return 0
                else:
                    return 1
                

        list= []
        for i in df.url:
            try:
                response = requests.get(i)
            except:
                response = ''
            forward = forwading(response)
            list.append(forward)
        df['Web_Forwards'] = list
        df.to_csv('test1.csv',index=False)
        
        def certTO(messages):
            try:
                hostname = messages
                ctx = ssl.create_default_context()
                with ctx.wrap_socket(socket.socket(), server_hostname=hostname) as s:
                    s.connect((hostname, 443))
                    cert = s.getpeercert()

                subject = dict(x[0] for x in cert['subject'])
                issued_to = subject['commonName']
                if issued_to=="":
                    return 1
                else:
                    return 0
            except:
                issued_to = "No certification Informations"
                return 1
            
        list=[]
        for i in df.url:
            i = urlparse(i).netloc
            c1 = certTO(i)
            list.append(c1)
        df['cert_to']=list
        df.to_csv('test1.csv',index=False)    

        def certBY(messages):
            try:
                hostname = messages
                ctx = ssl.create_default_context()
                with ctx.wrap_socket(socket.socket(), server_hostname=hostname) as s:
                    s.connect((hostname, 443))
                    cert = s.getpeercert()

                issuer = dict(x[0] for x in cert['issuer'])
                issued_by = issuer['commonName']
                if issued_by == "":
                    return 1
                else:
                    return 0
            except:
                issued_by = "No certification Information"
                return 1
            
        list=[]
        for i in df.url:
            i = urlparse(i).netloc
            c2 = certTO(i)
            list.append(c2)
        df['cert_by']=list
        df.to_csv('test1.csv',index=False) 
        
        #predict using feature based trained model
        pf1 = pd.read_csv('test1.csv')
        pf = pf1.drop(['url'],axis=1).copy()
        x = pf.values.reshape(1,16,1)
        #y = modelfeature.predict(x)
        y = modelfeature.predict(x)
        
        ## URL certification
        def certTO(messages):
            try:
                hostname = messages
                ctx = ssl.create_default_context()
                with ctx.wrap_socket(socket.socket(), server_hostname=hostname) as s:
                    s.connect((hostname, 443))
                    cert = s.getpeercert()
        
                subject = dict(x[0] for x in cert['subject'])
                issued_to = subject['commonName']
                return issued_to
            except:
                issued_to = "No certification Informations"
                return issued_to
            
        def certBY(messages):
            try:
                hostname = messages
                ctx = ssl.create_default_context()
                with ctx.wrap_socket(socket.socket(), server_hostname=hostname) as s:
                    s.connect((hostname, 443))
                    cert = s.getpeercert()
        
                issuer = dict(x[0] for x in cert['issuer'])
                issued_by = issuer['commonName']
                return issued_by
            except:
                issued_by = "No certification Information"
                return issued_by
            
        
        issued_to = certTO(messages)
        issued_by = certBY(messages)

        
        #integrating virus total
        def scan_url(url):
            api_url = 'https://www.virustotal.com/vtapi/v2/url/scan'
            params = {'apikey': API_KEY, 'url': url}

            response = requests.post(api_url, data=params)
            result = response.json()

            if 'scan_id' in result:
                print(f"Scan ID: {result['scan_id']}")
                return result['scan_id']
            elif 'verbose_msg' in result:
                print(f"Error: {result['verbose_msg']}")
            else:
                print("Unknown error")

        def get_report(scan_id):
            scan_results = []
            api_url = 'https://www.virustotal.com/vtapi/v2/url/report'
            params = {'apikey': API_KEY, 'resource': scan_id}

            response = requests.get(api_url, params=params)
            result = response.json()
            

            if result['response_code'] == 1:
                positives = result['positives']
                total = result['total']
                scan_date = result['scan_date']

                print(f"Scan Results: {positives}/{total}")
                print(f"Scan Date: {scan_date}")
                print("Scan Engines:")
                
            for engine, result in result['scans'].items():
                scan_results.append({"engine": engine, "result": result['result']})
                print(f"  {engine}: {result['result']}")
                
                #return engine, result
            else:
                print("Scan not finished or URL not found")
            return positives, total, scan_results
                
        scan_id = scan_url(messages)
        
        if scan_id:
            
            positives, total, scan_results = get_report(scan_id)
    
        
 #######################################################################################       
        
        if a==1:
            showmsg1 = '';
            y_pred = '';
            classes_y = '';
            y= '';
            urlstatus='';
    
        #return render_template('index.html', prediction_text='url prediction -{}'.format(classes_y))
    return render_template('index.html',status_value=status,hidden_msg=showmsg1 ,prediction_text=format(y_pred),prediction_text1=format(classes_y),urlstatus=urlstatus,URL_issued_by=format(issued_by),
                           URL_issued_to=format(issued_to),created_date=createdDate,expired_date=expiredate
                           ,domain_age = domainAge,featurebase_predict=y,ip_in_url=havingip,at_in_url=havingat2, url_length=urllength2,url_depth=urldepth2,url_redirect=urlredirection2, url_https=urlhttps, url_tiny=urltiny, url_prefix=urlprefix, url_dnsrecord=urldnsrecord, url_iframe=urliframe, url_forward=urlforward, url_mouseover=urlmouseover,
                           positives_html=positives, total_html=total, results_tuples = scan_results
                           )
           



if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8000, debug=True)
    
    
#app.run(host='0.0.0.0',port=8000, debug=True)

