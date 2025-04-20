
import pandas as pd
import requests


def data_import():
    # Fetch data from the API
    # url = "https://barbechli-api.onrender.com/api/v1/products/?sort_by=last_updated&sort_order=desc&skip=0&limit=2000"

    url = "https://barbechli-api.onrender.com/api/v1/products/?sort_by=last_updated&sort_order=desc&skip=0&limit=2000"

    response = requests.get(url)

    # Parse JSON response
    data = response.json()

    # Convert to DataFrame
    df = pd.DataFrame(data['items'])

    df.drop(columns=['category', 'subcategory', 'currency','source_name'],axis=0 ,inplace=True)
    ids_amd=df[df['brand']=='amd'] .index.tolist()

    for i in ids_amd:
      df['brand'].iloc[i]=df['title'].iloc[i].split(' ')[2]

    ids_nvd=df[df['brand']=='nvidia'] .index.tolist()

    for i in ids_nvd:
      df['brand'].iloc[i]=df['title'].iloc[i].split(' ')[2]

    df['brand'][df['brand']=='m']='apple'
    df['brand'][df['brand']=='mba']='apple'
    df['brand'][df['brand']=='ACER']='acer'
    df['brand'][df['brand']=='hz']='acer'
    df['brand'][df['brand']=='i']='dell'
    df['brand'][df['brand']=='rtx']='asus'
    df['brand'][df['brand']=='windows']='asus'
    df['brand'][df['brand']=='ASUS']='asus'
    df['brand'][df['brand']=='icon']='msi'
    df['brand'][df['brand']=='gpu']='msi'
    df['brand'][df['brand']=='badge']='lenovo'
    df['brand'][df['brand']=='geforce']='lenovo'
    df['brand'][df['brand']=='LENOVO']='lenovo'
    return df

