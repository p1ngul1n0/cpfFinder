from aiohttp import ClientSession
from base64 import b64decode
from bs4 import BeautifulSoup
from colorama import init, Fore, Style, Back
import asyncio
import json
import argparse

init()
lookupFilename = 'data.json'


print(f'''{Fore.GREEN}

   __________  _______           __         
  / ____/ __ \/ ____(_)___  ____/ /__  _____
 / /   / /_/ / /_  / / __ \/ __  / _ \/ ___/
/ /___/ ____/ __/ / / / / / /_/ /  __/ /    
\____/_/   /_/   /_/_/ /_/\__,_/\___/_/     
                                            

''')
                                            

parser = argparse.ArgumentParser()
parser.add_argument('-cpf', action = 'store', dest='cpf',
                           required = False,
                           help = 'CPF alvo.')
parser.add_argument('--noisy',action='store_false', dest='stealthMode', help='Busca CPF em sites que podem causar alguma ação como envio de e-mails ou SMS, alertando o alvo.')
parser.add_argument('--show-all',action='store_true', dest='showAll', help='Mostrar todos resultados, mesmo que não resultem em uma conta identificada.')
arguments = parser.parse_args()

proxy = "http://127.0.0.1:8080"

async def doRequest(lookup, cpf, stealthMode, showAll):
    appName = decode64(lookup['app'])
    jsonBody = None
    formData = None
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.0; rv:40.0) Gecko/20100101 Firefox/40.0"
    }
    url = decode64(lookup['url']).replace('{cpf}', str(cpf))
    if 'formatted' in lookup and lookup['formatted']:
        cpf = '{}.{}.{}-{}'.format(cpf[:3], cpf[3:6], cpf[6:9], cpf[9:])
    if 'headers' in lookup:
        headers.update(eval(decode64(lookup['headers'])))
    if 'json' in lookup:
        jsonBody = json.loads(decode64(lookup['json']).replace('{cpf}', str(cpf)))
    if 'form' in lookup and '{cpf}' in decode64(lookup['form']):
        formData = decode64(lookup['form']).replace('{cpf}', str(cpf))
    
    if lookup['silent'] == False and stealthMode:
        pass
    else:
        try:
            async with ClientSession() as session:
                async with session.request(method=lookup['method'], url=url, json=jsonBody, data=formData, headers=headers, ssl=False) as response:
                    responseContent = await response.text()
                    if 'content-type' in response.headers and "application/json" in response.headers["Content-Type"]:
                        jsonData = await response.json()
                    else:
                        soup = BeautifulSoup(responseContent, 'html.parser')
                    if eval(lookup["valid"]):
                        print (f'{Fore.GREEN + Style.BRIGHT}[+]\033[0m {Fore.BLUE}{appName}\033[0m {Fore.BLACK + Style.BRIGHT}{url}\033[0m')
                        if 'returnData' in lookup:
                            print (f'  |-{Fore.BLACK + Back.WHITE}{eval(lookup["returnData"])}\033[0m')
                    elif showAll:
                        print (f'[-] {Fore.BLUE}{appName}\033[0m {Fore.BLACK + Style.BRIGHT}{url}\033[0m')
        except Exception as e:
            print (f'{Fore.RED + Style.BRIGHT}[x]\033[0m {Fore.BLUE}{appName}\033[0m {Fore.BLACK + Style.BRIGHT}{url}\033[0m')
            print(f'  |-{Fore.LIGHTRED_EX + Back.WHITE + Style.BRIGHT}{repr(e)}\033[0m')

def readLookups():
    file = open(lookupFilename)
    lookupsData = json.load(file)
    print (f"{Fore.WHITE}[-] Carregado {len(lookupsData['sites'])} sites de '{lookupFilename}'  \033[0m")
    return lookupsData

def decode64(encodedValue):
    decodedValue = b64decode(encodedValue).decode('UTF-8')
    return decodedValue

async def flyOver(cpf, stealthMode, showAll):
    lookupsData = readLookups()
    if stealthMode:
        print (f'{Fore.YELLOW + Style.DIM}[!] Modo silencioso ativo 🤫')
    else:
        print (f'{Fore.YELLOW + Style.DIM}[!] Modo barulhento ativo 🔊')
    print (f"{Fore.LIGHTYELLOW_EX + Style.BRIGHT}[!] Buscando o CPF '{cpf}' \033[0m")
    results = await asyncio.gather(*[
        doRequest(lookup, cpf, stealthMode, showAll)
        for lookup in lookupsData['sites']
    ])

if arguments.cpf:
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(flyOver(arguments.cpf, arguments.stealthMode, arguments.showAll))

