import requests
from bs4 import BeautifulSoup
import mysql.connector as mysql
from selenium import webdriver
import time

# =============================================================================
# ~connecting to MYSQL database
# =============================================================================

db = mysql.connect(
    host = "localhost",
    user = "Alex",
    password = "password",
    database = "rentschema"
    )

####

driver = webdriver.Chrome()
options = webdriver.ChromeOptions()
cursor = db.cursor()

options.add_argument('--headless')


# =============================================================================
# ~defining URL to scrape and parsing it
# =============================================================================
URL = "https://www.fotocasa.es/es/alquiler/viviendas/castellon-provincia/todas-las-zonas/l?latitude=39.986&longitude=-0.037866&combinedLocationIds=724,19,12,0,0,0,0,0,0"

#URL = "https://www.fotocasa.es/es/alquiler/viviendas/onda/todas-las-zonas/l?latitude=39.9654&longitude=-0.261905&combinedLocationIds=724,19,12,343,612,12084,0,0,0"

###TESTURL###
#URL = "https://www.fotocasa.es/es/alquiler/viviendas/castellon-provincia/todas-las-zonas/l?combinedLocationIds=724%2C19%2C12%2C0%2C0%2C0%2C0%2C0%2C0&latitude=39.986&longitude=-0.037866"
###TESTURL###


driver.get(URL)


privacy = driver.find_element_by_xpath('//*[@id="App"]/div[4]/div/div/div/footer/div/button[2]')
privacy.click()
time.sleep(1)

for x in range(10):
    driver.execute_script("window.scrollTo(0, %s)"%(1080*x))
    time.sleep(1)



driverurl = driver.page_source


page = requests.get(URL)
soup = BeautifulSoup(driverurl, "html.parser")


# =============================================================================
# ~finding the container that contains relevant data
# =============================================================================



errorcount = 0
results = soup.find("section", class_="re-Searchresult")

cards = results.find_all("article", class_="re-CardPackMinimal")

####

# =============================================================================
# ~scraper body
# =============================================================================


location_list = []
building_list = []
price_list = []
features_list = []

buildingstr_list = []
locationdata_list = []
priceint_list = []


for card in cards:
    try:
        # =============================================================================
        #     ~chosing relevant data to scrape
        # =============================================================================
        
        cardtitle = card.find("h3", class_="re-CardHeader")
        location = cardtitle.find("span", class_="re-CardTitle")
        building = location.find("span")
        price = cardtitle.find(class_="re-CardPriceComposite")
        
        ####
        
        # =============================================================================
        #     ~solving formatting problems for "price"
        # =============================================================================
        
        pricestr = str(price.text)
            
        if pricestr.__contains__("."):
            pricestr = pricestr.replace(".", "")
            
        
        priceint = int((pricestr[:-7]))
        
        # =============================================================================
        #     ~formatting the rest of the fields
        # =============================================================================
        
        buildingstr = str(building.text)
        locationstr = str(location.text)
        locationdata = ""
        
        if locationstr.find(",") != -1:
            locationdata = locationstr[locationstr.rfind(",")+1:]
            locationdata = locationdata.strip(" ")
        else:
            locationdata = locationstr.strip(" ")
            locationdata = locationdata[locationdata.rfind(" ")+1:]
        
        priceint_list.append(priceint)
        locationdata_list.append(locationdata)
        buildingstr_list.append(buildingstr)
        
        
        
        
        
        
        
        
        
       
        # =============================================================================
        #     ~chosing extra features to include in the database
        # =============================================================================
           
        
        
        
        feature = card.find("ul", class_="re-CardFeatures-wrapper")
        individual = feature.find_all("li") 
        
        individual_features_list = []
        
        for feat in individual:
            individual_features_list.append(feat.text)
            
        
        features_list.append(individual_features_list)
        ####
        
        # =============================================================================
        #     ~sorting features in individual lists to format them
        # =============================================================================
        
        
        bed_list = []
        bath_list = []
        meter_list = []
        extra_feature_list = []
    
        
        
        for x in features_list:
            for i in range(len(x)):
                
                if len(x) < 4:
                    x.append("")
            
     
        
            
        for bed, bath, meter, extra in features_list:
            
            if bed == None:
                bed = 0
            if bath == None:
                bath = 0
            if meter == None:
                meter = 0
            if extra == None:
                extra = ""    
            
            bed_list.append(bed)
            bath_list.append(bath)
            meter_list.append(meter)
            extra_feature_list.append(extra)
            
        
        ####
    except:
        
        print("1 record raised error")
        errorcount += 1
# =============================================================================
#     ~solving formatting problems for features
# =============================================================================
    print(features_list)
    
    bed_list_int = []
    bath_list_int = []
    meter_list_int = []
    
    for i in bed_list:
        try:
            i = str(i)
            i = int(i[0])
            bed_list_int.append(i)
        except:
            i = 0
            bed_list_int.append(i)

    for i in bath_list:
        try:
            i = str(i)
            i = int(i[0])
            bath_list_int.append(i)
        except:
            i = 0
            bath_list_int.append(i)
    
    for i in meter_list:
        try:
            i = str(i)
            i = int(i[:-3])
            meter_list_int.append(i)
        except:
            i = 0
            meter_list_int.append(i)
    
    
    
    # =============================================================================
    #     ~adding the rest of the features data to pertinent lists
    # =============================================================================
    
    
    
         
    location_list.append(location.text)
    building_list.append(building.text)
    price_list.append(priceint)
    
    
    ####
   
'''   
print(bed_list_int)
print(bath_list_int)
print(meter_list_int)
print(extra_feature_list)
    
print(location_list)
print(building_list)
print(price_list)
'''
    
# =============================================================================
#     ~Preparing data to be database ready -1-
#       sorting features data back to its original order
# =============================================================================

bed_tuple = tuple(bed_list_int)
bath_tuple = tuple(bath_list_int)
meter_tuple = tuple(meter_list_int)
extra_tuple = tuple(extra_feature_list)

list_of_tuples = [bed_tuple, bath_tuple, meter_tuple, extra_tuple]

forrange = None
for i in list_of_tuples:
    forrange = len(i)

finaldatalist = []
provisionallist = []
count = 0

for x in range(forrange):
    print("property", x)
    for i in list_of_tuples:
        print(i[x])
        provisionallist.append(i[x])
        if type(i[x]) == str:
            finaldatalist.append(provisionallist)
            provisionallist = []


         


feature_results_tuple = tuple(finaldatalist)
print(feature_results_tuple)   

# =============================================================================
#      ~Preparing data to be database ready -2-
#       
# =============================================================================

print("RELEVANT DATA")

building_tuple = tuple(buildingstr_list)
location_tuple = tuple(locationdata_list)
price_tuple = tuple(priceint_list)

list_of_tuples2 = [building_tuple, location_tuple, price_tuple]

forrange2 = None

for i in list_of_tuples2:
    forrange2 = len(i)

finaldatalist2 = []
provisionallist2 = []
count2 = 0

print(list_of_tuples2)

for x in range(forrange2):
    print("property", x)
    for i in list_of_tuples2:
        print(i[x])
        provisionallist2.append(i[x])
        if type(i[x]) == int:
            finaldatalist2.append(provisionallist2)
            provisionallist2 = []


data_results_tuple = tuple(finaldatalist2)
print(data_results_tuple)

# =============================================================================
#     ~inserting all data in the database
# =============================================================================


propertiesquery = "INSERT INTO properties (property, location, price) VALUES (%s, %s, %s)"

cursor.executemany(propertiesquery, data_results_tuple)
       
db.commit()
    
print(cursor.rowcount, "records inserted in properties")



    
 
featurequery = "INSERT INTO feature (bedrooms, baths, squarem, extra) VALUES (%s, %s, %s, %s)"


cursor.executemany(featurequery, feature_results_tuple)

db.commit()

print(cursor.rowcount, "records inserted in features")
 
print(errorcount, "records raised error")






