from django.shortcuts import render
from django.contrib import messages 
from django.views import View 

from .forms import IpForm

import asyncio 
import aiohttp
import json 

import requests 
import regex 
import html2text 



# thirdparty api urls 
ip_fraud_score_url = "https://scamalytics.com/ip"
ip_locate_url = "http://ip-api.com/batch"

# regex pattern for extracting json from html data 
pattern = regex.compile(r'\{(?:[^{}]|(?R))*\}')

# async function to get ip fraud score 
async def get_fraud_score(url: str, ip: str) -> str:

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{url}/{ip}") as response:
            api_response = await response.text() 
            html_reponse_text = html2text.html2text(api_response)
            clean_html_text = pattern.findall(html_reponse_text)
            final_result = clean_html_text[0]

            return final_result


# async function to get ip address information
async def get_ip_info(url: str, address_list: str) -> list:

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=address_list) as response:
            api_response = await response.json()
            api_data = json.dumps(api_response[0])
            json_data = json.loads(api_data)
            
            return json_data


# home view 
class HomeView(View):
    
    # http get function 
    async def get(self, request):
        form = IpForm()
        return render(request, 'home.html', {'form':form})
    
    # http post function 
    async def post(self, request):
        ip_score = ""
        ip_score_error = ""
        ip_info = []
        ip_info_error = " "
        ip_address_list = []

        form = IpForm(request.POST)

        # check if form is valid 
        if form.is_valid():
            ip_address = form.cleaned_data['ip_address']
            # append ip_address_list with ip_address
            ip_address_list.append(ip_address)

            try:
                ip_score = await get_fraud_score(ip_fraud_score_url, ip_address)

            except:
                ip_score_error = "ip fraud score is not available!"
            
            try:
                ip_info = await get_ip_info(ip_locate_url, ip_address_list)
            except:
                ip_info_error = "unable to get ip address info"

            if ip_score and ip_info:
                messages.success(request,"Got Ip fraud score and Ip info")
                
                context = {
                    "ip_score":ip_score,
                    "ip_status":ip_info["status"],
                    "country":ip_info["country"],
                    "country_code":ip_info["countryCode"],
                    "region":ip_info["region"],
                    "region_name":ip_info["regionName"],
                    "city":ip_info["city"],
                    "zip":ip_info["zip"],
                    "latitude":ip_info["lat"],
                    "longitude":ip_info["lon"],
                    "timezone":ip_info["timezone"],
                    "isp":ip_info["isp"],
                    "isp_org":ip_info["org"],
                    "isp_ass":ip_info["as"],
                    "form":form
                }
                return render(request, 'home.html', context=context)
            
            elif ip_score and not ip_info:
                messages.info(request, "Could not get IP Info")
                return render(request, 'home.html', {"ip_score":ip_score, "ip_info_error":ip_info_error, "form":form})
            
            elif ip_info and not ip_score:
                messages.info(request, "Could not get IP Score")
                
                context = {
                    "ip_score":ip_score,
                    "ip_status":ip_info["status"],
                    "country":ip_info["country"],
                    "country_code":ip_info["countryCode"],
                    "region":ip_info["region"],
                    "region_name":ip_info["regionName"],
                    "city":ip_info["city"],
                    "zip":ip_info["zip"],
                    "latitude":ip_info["lat"],
                    "longitude":ip_info["lon"],
                    "timezone":ip_info["timezone"],
                    "isp":ip_info["isp"],
                    "isp_org":ip_info["org"],
                    "isp_ass":ip_info["as"],
                    "ip_score_error":ip_score_error,
                    "form":form
                }

                return render(request, 'home.html', context=context)
            
            else:
                messages.error(request, "Could not get IP score and info")
                return render(request, 'home.html', {"ip_info_error":ip_info_error, "ip_score_error":ip_score_error, "form":form})

        
        form = IpForm()
        messages.error(request, "invalid input")
        return render(request, 'home.html', {'form':form})
    


    

    


