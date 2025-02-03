import requests
import base64
import xml.etree.ElementTree as ET
import xml.dom.minidom

from datetime import datetime

client_id = ""
client_secret = ""
auth_token = ""
access_token = ""
endpoint = ""
month=1

def active_access_token():
    url = f"{endpoint}/rest/auth/token/"
    
    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    data = {
        "grantType": "authorization_code",
        "token": auth_token
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 201:
        return response.json()
    if response.status_code == 401:
        return
    else:
        return response.text

def get_finanse_documents(access_token):
    url = f"{endpoint}/rest/api/finance/documents/"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        return response.text

def create_invoice_xml(documents, month_filter=None):
    root = ET.Element("Invoices")
    
    for doc in documents["documents"]:
        sold_date = datetime.strptime(doc["soldAt"], "%Y-%m-%dT%H:%M:%S%z")
        if month_filter and sold_date.month != month_filter:
            continue
        
        invoice = ET.SubElement(root, "Invoice")
        ET.SubElement(invoice, "DocumentNumber").text = doc["documentNumber"]
        ET.SubElement(invoice, "TotalWithTax").text = doc["originalAmountTotalWithTax"]
        ET.SubElement(invoice, "TotalWithoutTax").text = doc["originalAmountTotalWithoutTax"]
        ET.SubElement(invoice, "Currency").text = doc["originalCurrency"] or "PLN"
        ET.SubElement(invoice, "CreatedAt").text = doc["createdAt"]
        ET.SubElement(invoice, "InvoicedAt").text = doc["invoicedAt"]
        ET.SubElement(invoice, "SoldAt").text = doc["soldAt"]
        
        receiver = ET.SubElement(invoice, "Receiver")
        ET.SubElement(receiver, "Name").text = doc["documentReceiver"]["name"]
        ET.SubElement(receiver, "Street").text = doc["documentReceiver"]["streetName"]
        ET.SubElement(receiver, "City").text = doc["documentReceiver"]["city"]
        ET.SubElement(receiver, "ZipCode").text = doc["documentReceiver"]["zipCode"]
        ET.SubElement(receiver, "Country").text = doc["documentReceiver"]["country"]
        
        issuer = ET.SubElement(invoice, "Issuer")
        ET.SubElement(issuer, "Name").text = doc["documentIssuer"]["name"]
        ET.SubElement(issuer, "Street").text = doc["documentIssuer"]["streetName"]
        ET.SubElement(issuer, "City").text = doc["documentIssuer"]["city"]
        ET.SubElement(issuer, "ZipCode").text = doc["documentIssuer"]["zipCode"]
        ET.SubElement(issuer, "Country").text = doc["documentIssuer"]["country"]
        
        items = ET.SubElement(invoice, "Items")
        for item in doc["documentItems"]:
            item_element = ET.SubElement(items, "Item")
            ET.SubElement(item_element, "Name").text = item["name"]
            ET.SubElement(item_element, "PriceWithTax").text = item["originalPriceWithTax"]
            ET.SubElement(item_element, "PriceWithoutTax").text = item["originalPriceWithoutTax"]
            ET.SubElement(item_element, "Tax").text = item["tax"]
            ET.SubElement(item_element, "Quantity").text = str(item["quantity"])
        
    xml_str = xml.dom.minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    with open(f"invoices-{month}.xml", "w", encoding="utf-8") as f:
        f.write(xml_str)

def main():
    active_access_token()
    documents = get_finanse_documents(access_token)
    create_invoice_xml(documents, month)

if __name__ == "__main__":
    main()
