__author__ = 'Callum'
# -*- encoding: utf-8 -*-
#Python 3.7
#pax_describe_source.py - Will look at where the data has been imported from, and add that to the library description
#Version: 0.1
#Date: August 26th 2019

import requests, json, time
from requests.auth import HTTPBasicAuth
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options 

#*****************THESE ARE YO VARIABLES - YOU NEED TO EDIT THESE *******
paxata_url = "http://localhost:8080"
paxata_restapi_token = "95042539cd3e430c83bf7000a5c9d6c9"

def update_description_for_all_library_items(authorization_token, paxata_url, driver):
    successfullyDescriptionsCounter = 0

    # Step 1 - Get the library datasets
    print("Fetching library info.")
    getLibraryRequest = (paxata_url + "/rest/library/data")
    getLibraryResponse = requests.get(getLibraryRequest, auth=authorization_token, verify=True)
    if (getLibraryResponse.ok):
        getLibraryJsonResponse = json.loads(getLibraryResponse.content)
        for item in getLibraryJsonResponse:
            #loop through the library id's one at a time
            dataFileId = str(item.get('dataFileId'))
            version = str(item.get('version'))
            description = str(item.get('description'))
            datasource = str(item.get('source'))
            columnCount = str(item.get('columnCount'))
            rowCount = str(item.get('rowCount'))
            compressionType = str(item.get('source').get('compressionType'))
            dataType = str(item.get('source').get('type'))
                        
            #Step 2 - If the dataset does not contain a description, then update it with the datasource
            if not description:
                #go to the page to update the description
                time.sleep(1)
                library_metadata_page = paxata_url + "/#/library/setup/" + dataFileId + "/" + version + "/meta"
                driver.get(library_metadata_page) 
                #once we know the description isn't blank check if it's a local file or a connector
                if (dataType == "Connector"):
                    # Next we need to check if the connectorId contains multiple ids (sometimes it does for some reason?)
                    connectorId = item.get('source').get('metadata').get('connectorId')
                    my_list_of_connectors = connectorId.split(",")
                    for connector in my_list_of_connectors:
                        getConnectorRequest = (paxata_url + "/rest/connector/configs/"+connector)
                        getConnectorResponse = requests.get(getConnectorRequest, auth=authorization_token, verify=True)
                        if (getConnectorResponse.ok):
                            getConnectorJsonResponse = json.loads(getConnectorResponse.content)
                            name = ""
                            name = getConnectorJsonResponse.get('name')
                            #check if it's a jdbc connector or not (because there is extra info that might be useful)
                            uri = ""
                            if getConnectorJsonResponse.get('options'):
                                # i might need to add a "try" here (for other sources that have "options" but aren't jdbc)
                                uri =  getConnectorJsonResponse.get('options').get('jdbc.uri')
                            # check if one of the connector ids is null, otherwise, assume it is the correct one.
                            if name and uri:
                                time.sleep(1)
                                driver.find_element_by_xpath("//*[@id=\"dataFileForm\"]/div/div/div/div[2]/div/div[2]/div[2]/div/div/input").send_keys(dataType + " - " + name + " ("+ "URI=" +uri+")")   
                                driver.find_element_by_xpath("//*[@id=\"add_data_set_button\"]").click()
                            else:
                                if name:
                                    time.sleep(1)
                                    driver.find_element_by_xpath("//*[@id=\"dataFileForm\"]/div/div/div/div[2]/div/div[2]/div[2]/div/div/input").send_keys(dataType + " ("+ "Compression=" +compressionType+")")   
                                    driver.find_element_by_xpath("//*[@id=\"add_data_set_button\"]").click()
                else:
                    #it's a local file
                    time.sleep(1)
                    driver.find_element_by_xpath("//*[@id=\"dataFileForm\"]/div/div/div/div[2]/div/div[2]/div[2]/div/div/input").send_keys(dataType + " ("+ "Compression=" +compressionType+")")   
                    driver.find_element_by_xpath("//*[@id=\"add_data_set_button\"]").click()                    
                #description XPATH
                # /html/body/ui-view/div/div[2]/ui-view/div/div/div[3]/div[2]/ui-view/ui-view/div/div[2]/div/ui-view/form/div/div/div/div[2]/div/div[2]/div[2]/div/div/input
                successfullyDescriptionsCounter+=1

    print ("Updated Descriptions for " + str(successfullyDescriptionsCounter) + " Library items")
    return

def sitelogin(authorization_token,paxata_url):
    #driver = webdriver.Firefox()
    chrome_options = Options()  
    chrome_options.add_argument("--headless")  
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path="/Users/callumfinlayson/Documents/Paxata/development/python/pax-describe-source/chromedriver")    
    driver.get(paxata_url)    
    try:
        time.sleep(2)
        print("*******")
        #Username on Paxata site:
        driver.find_element_by_xpath("/html/body/div[4]/div/div/form/div[3]/input").send_keys("callum")
        #Password on Paxata site:
        driver.find_element_by_xpath("/html/body/div[4]/div/div/form/div[4]/input").send_keys("Paxata1!")
        #Submit button on Paxata site:
        driver.find_element_by_xpath("/html/body/div[4]/div/div/form/div[5]/button").click()
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print (message)
    #loop through library items (if they don't have a description, create a description based on their datasource)
    update_description_for_all_library_items(authorization_token,paxata_url,driver)
    driver.close()

########### Main Program ################
if __name__ == '__main__':    
    authorization_token = HTTPBasicAuth("",paxata_restapi_token)
    sitelogin(authorization_token,paxata_url)
