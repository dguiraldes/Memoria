
# coding: utf-8

# In[1]:


from fuzzywuzzy import process,fuzz
import pandas as pd


# In[2]:


def TopMatches(name,nlist,min_score=50):
    dscore=-1
    matchlist=[]
    for name2 in nlist:
        score=fuzz.partial_ratio(name,name2)
        if score >=min_score:
            dscore=score
            matchlist.append((name2,dscore))
    return matchlist


# In[3]:


def best_mean_ratio(name,matchlist,min_score=80):
    max_mean_score=-1
    best_match=''
    for tup in matchlist:
        mean_score=0
        mean_score+=tup[1]
        mean_score+=fuzz.ratio(name,tup[0])
        mean_score+=fuzz.token_sort_ratio(name,tup[0])
        mean_score+=fuzz.token_set_ratio(name,tup[0])
        if mean_score/4>max_mean_score and mean_score/4>=min_score:
            max_mean_score=mean_score
            best_match=tup[0]
    return best_match


# In[4]:


def fancy_list(df):
    fancy_df=df.str.upper()
    fancy_df=fancy_df.str.replace('.','')
    fancy_df=fancy_df.str.replace('_',' ')
    return fancy_df


# In[6]:


def dataInput(csvfile):
    data=pd.read_csv(csvfile,encoding='utf-8')
    data['Descripcion_fancy']=fancy_list(data['Descripcion'])
    data['Asignado']=fancy_list(data['Asignado'])
    data=data[['Descripcion','Descripcion_fancy','Asignado','Sector']]
    return data


# In[7]:


if __name__ == "__main__":
    data=dataInput('Correccion_clientes_v5.csv')
    for i in range(0,len(data)):
        if pd.isnull(data.iloc[i,2]):
            clist=list(data.Descripcion_fancy)
            client=clist.pop(i)
            matchlist=TopMatches(client,clist)
            if len(matchlist)>1:
                best_match=best_mean_ratio(client,matchlist)
                if best_match=='':
                    data.iloc[i,2]=client
                else:
                    idx=data[data.Descripcion_fancy==best_match].index[0]
                    data.iloc[i,2]=data.iloc[idx,2]
            elif len(matchlist)==1:
                idx=data[data.Descripcion_fancy==matchlist[0][0]].index[0]
                data.iloc[i,2]=data.iloc[idx,2]
            else:
                data.iloc[i,2]=client
    data=data.drop(columns=['Descripcion_fancy'])
    data.to_csv('Clientes_reasignados5.csv',index=False, encoding='utf-8')

