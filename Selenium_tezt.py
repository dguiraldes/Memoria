
# coding: utf-8

# In[1]:


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from fuzzywuzzy import process


# In[2]:


class Selenium_window:
    
    def __init__(self):    
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(chrome_options=options,executable_path=r'//mnt//c//Users//ep_dguiraldes//chromedriver.exe')
        self.currentTab=0
    
    def webPage(self,url):
        driver=self.driver
        driver.get(url)
        time.sleep(2)
   
    def login(self,em,pas):
        sesion=self.driver.find_element_by_xpath("/html/body/nav/div/ul[1]/li[5]/a")
        sesion.click()
        time.sleep(1)
        email=sel.driver.find_element_by_id("email")
        password=sel.driver.find_element_by_id("password")
        email.send_keys(em)
        password.send_keys(pas)
        password.send_keys(Keys.ENTER)
        time.sleep(2)

    def search(self,name,sbar='s'):
        search_bar=self.driver.find_element_by_name(sbar)
        search_bar.clear()
        time.sleep(1)
        search_bar.send_keys(name)
        search_bar.send_keys(Keys.ENTER)
        time.sleep(2)
    
    def findResults(self):
        results=self.driver.find_element_by_id('results-content')
        rlist=results.text.split('\n')
        return rlist
   
    def switchTab(self,n):
        self.driver.switch_to.window(sel.driver.window_handles[n])
        self.currentTab=n
        time.sleep(3)
    
    def createNameDict(self,rlist):
        d={}
        for nameLine in rlist:
            kind,name,rut=self.splitLine(nameLine)
            if kind=='Empresas':
                d[name]=rut
        return d
    
    def splitLine(self,nameLine):
        lineList=nameLine.split(' ')
        rut=lineList.pop(0)
        kind=lineList.pop(len(lineList)-1)
        name=' '.join(lineList)
        return (kind,name,rut)
        
    def findBestMatch(self,name,nameDict):
        nameList=list(nameDict.keys())
        bestMatch=process.extractOne(name,nameList)[0]
        rut=nameDict[bestMatch]
        return bestMatch,rut
    
    def goToMatchTab(self,bestMatch):
        name=bestMatch[0]
        rut=bestMatch[1]
        rutLink=self.driver.find_element_by_link_text(rut)
        rutLink.click()
        time.sleep(3)
        
    def inspectMatchTab(self,xpath):
        self.currentTab+=1
        self.switchTab(self.currentTab)
        info=self.driver.find_element_by_xpath(xpath)
        return info.text
    
    def notFound(self,name):
        self.driver.execute_script("window.open('');")
        time.sleep(3)
        self.switchTab(1)
        self.driver.get("https://www.google.com")
        self.search(name,sbar='q')
        rut=''
        try:
            loc=self.driver.find_element_by_partial_link_text('www.mercantil.com')
            loc.click()
            time.sleep(3)
            box=self.driver.find_element_by_xpath("//*[@id='caja_detalle']/div[1]")
            contents=box.text.split('\n')
            rut_idx=contents.index('Rut')
            rut=contents[rut_idx+1]
        except:
            pass
        self.tearDown()
        time.sleep(1)
        self.switchTab(0)
        return rut
        
    def findInfoByRut(self,rut):
        self.search(rut)
        rlist=self.findResults()
        if 'No se han encontrado resultados' in rlist[0]:
            return ('N/A','','')
        else:
            Match=self.splitLine(rlist[0]) #kind,name,rut
            bestMatch=(Match[1],Match[2])
            self.goToMatchTab(bestMatch)
            time.sleep(3)
            sector=self.inspectMatchTab("//*[@id='results-content']/tr[4]/td[2]")
            self.tearDown()
            self.switchTab(0)
            return (bestMatch[0],bestMatch[1],sector)
        
    
    def findInfo(self,name):
        self.search(name)
        rlist=self.findResults()
        if 'No se han encontrado resultados' in rlist[0]:
            rut=self.notFound(name)
            if rut=='':
                return ('N/A','','')
            else:
                return self.findInfoByRut(rut)
        else:
            nameDict=self.createNameDict(rlist)
            if nameDict=={}:
                return ('N/A','','')
            else:
                bestMatch=self.findBestMatch(name,nameDict)
                self.goToMatchTab(bestMatch)
                sector=self.inspectMatchTab("//*[@id='results-content']/tr[4]/td[2]")
                self.tearDown()
                self.switchTab(0)
                return (bestMatch[0],bestMatch[1],sector)
    
    def tearDown(self):
        self.driver.close()
        time.sleep(1)
        


# In[3]:


def repeated(name,nlist):
    idxList=[]
    for i in range(0,len(nlist)):
        if name==nlist[i]:
            idxList.append(i)
    return idxList

def assign(i,foundTuple,sset):
    fname,rut,sector=foundTuple
    sset.iloc[i,3]=fname
    sset.iloc[i,4]=rut
    sset.iloc[i,5]=sector
    try:
        sset.iloc[i,2]=sectorDict[sector]
    except KeyError:
        pass


# In[4]:


def mainRoutine():
    global sset
    global last_i
    for i in range(last_i,len(sset)):
        if pd.isnull(sset.iloc[i,2]):
            name=sset.iloc[i,1]
            foundTuple=sel.findInfo(name)
            idxList=repeated(name,sset.Asignado)
            for j in idxList:
                assign(j,foundTuple,sset)
        last_i=i


# In[5]:


sectorDict={
    'AGRICULTURA, GANADERIA, CAZA Y SILVICULTURA':'AGCS',
    'PESCA':'PESC',
    'EXPLOTACION DE MINAS Y CANTERAS':'MINE',
    'INDUSTRIAS MANUFACTURERAS NO METALICAS':'IMNM',
    'INDUSTRIAS MANUFACTURERAS METALICAS':'IMM',
    'SUMINISTRO DE ELECTRICIDAD, GAS Y AGUA':'SEGA',
    'CONSTRUCCION':'CONS',
    'COMERCIO AL POR MAYOR Y MENOR, REP. VEH.AUTOMOTORES/ENSERES DOMESTICOS':'COME',
    'HOTELES Y RESTAURANTES':'HORE',
    'TRANSPORTE, ALMACENAMIENTO Y COMUNICACIONES':'TRAC',
    'INTERMEDIACION FINANCIERA':'FINA',
    'ACTIVIDADES INMOBILIARIAS, EMPRESARIALES Y DE ALQUILER':'AIEA',
    'ADM. PUBLICA Y DEFENSA, PLANES DE SEG. SOCIAL AFILIACION OBLIGATORIA':'ADPD',
    'ENSE?ANZA':'ENSE',
    'ENSEÑANZA':'ENSE',
    'SERVICIOS SOCIALES Y DE SALUD':'SOSA',
    'OTRAS ACTIVIDADES DE SERVICIOS COMUNITARIAS, SOCIALES Y PERSONALES':'OTRO',
    'CONSEJO DE ADMINISTRACION DE EDIFICIOS Y CONDOMINIOS':'EDCO',
    }


# In[ ]:


if __name__ == "__main__":
    user= #user
    password= #password
    sel=Selenium_window()
    sel.webPage('http://www.genealog.cl')
    sel.search('')
    sel.login(user,password)

    sset=pd.read_csv('Clientes_reasignados5.csv',encoding='utf-8')
    sset['Nombre encontrado']=''
    sset['rut']=''
    sset['sector completo']=''
    last_i=0
    
    while last_i<len(sset):
        try:
            mainRoutine()
        except:
            time.sleep(5)
            last_i=last_i+1
            sel.currentTab=0

    sel.tearDown()
    sset.to_csv('output5.csv',encoding='utf-8',index=False)

