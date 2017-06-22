#-*- coding: utf-8 -*-
# Keven Aderson, Antonio Baptista e Rafael Pavarini
import json
import requests
import re
import datetime
import array

import sys
sys.stdout = open('teste.txt', 'w') #cria arquivo para armazenar datas e links selecionados esse arquivo ira conter objetos Json


hoje = datetime.date.today() # data de hoje que sera usada como parâmetro
#url do json no diario livre com filtro de uma semana compesquisa audiencia publica
url = 'http://devcolab.each.usp.br/do/catalog.json?f%5Bdata%5D%5B%5D=week_1&per_page=100&q=audiencia+publica'

#exemplo formato do objeto Json:
#id  "2017/05/31/565"
#data    "2017-05-31T00:00:00Z"
#retranca    "fafaadm"
#tipo_conteudo   "CÂMARA MUNICIPAL"
#secretaria  "CÂMARA MUNICIPAL - GABINETE DO"
#orgao   "SECRETARIA DAS COMISSÕES – SGP-1"
#texto   "((TITULO))COMISSÃO EXTRA…ograma Defesa das Águas"

#Metodos auxiliares

#passar a tipo como raw string usando antes dela r'
def verifica_resultado_busca(texto, padrao):
    #padrao = raw_imput(padrao)
    if re.search(padrao, texto) is None:
        return None
    return "has"

#converte id(string) em um indice(int)
def retorna_indice(id_obj):
    pedaco = id_obj.replace('/', '')
    pedaco = int(pedaco)
    return pedaco

#passando uma lista de supeitos ou seja datas que talvez sejam de audiencia publica
#acha uma data possivel ou seja datas maiores que o dia que estamos, tipo 0 apenas digitos, tipo 1 datas em extenso 
#e retorna uma lista com objeto do tipo datatime
def filtra_data(suspeitos):
    datas = [] #possiveis datas ficaram armazenadas aqui
    #formatos alphanumerico
    if len(suspeitos)>0:
        if len(suspeitos[0])>0: # caso lista vazia ou suspeito não exista ignora
            for suspeito in suspeitos[0]:
                if not suspeito:
                   continue
                numerosDatas = re.split(r'\/', suspeito) #converte uma data no formato exemplo: dd/mm/aaa em numero(int)
                dia = int(numerosDatas[0])  #atraves da posições da string acho digitos corresponte a dia e ao mes e ano
                mes = int(numerosDatas[1])
                if len(numerosDatas[2]) < 3:
                    numerosDatas[2] = "20"+numerosDatas[2]
                ano = int(numerosDatas[2])
                data_filtrada = datetime.date(ano, mes, dia) #armazena eles em um objeto datatime
                #se não for atual ignora
                if hoje < data_filtrada:
                    datas.append(data_filtrada)
                   
            
         # mesmo processo anterior porem para formatos escritos           
        if len(suspeitos[1])>0:
           meses = {'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4, 'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12}
           for suspeito in suspeitos[1]:
                if not suspeito:
                    continue
                numerosDatas = re.split(' ', suspeito)
                dia = int(numerosDatas[0])
                mes = mes = int(meses[numerosDatas[2]])
                ano = int(numerosDatas[4]) 
                data_filtrada = datetime.date(ano, mes, dia)
                
                if hoje < data_filtrada:
                    datas.append(data_filtrada)
                    
        if len(datas)>0:
           return datas
        else:
           return None # caso não exita nenhuma data possivel retorna none
           
           
def main():
    #pega json do servisdor
    r = requests.get(url)
    if r.status_code == 200:
        reddit_data = json.loads(r.content)
    else: 
        print("Tem algo bugado")
    #filtrando o que realmente é audiencia publica do executivo e adiconando
    audiencias = {} #contem todos obejtos da lista de docs ou seja o texto tipo de conteudo, sendo que cada um possui um id unico
    datas = {}       #contem possiveis datas associadas ao id
    links = {}      #links associado ao ids 
    for nota in  reddit_data['response']['docs']:
        tipo_conteudo = str(nota['tipo_conteudo'])
        if verifica_resultado_busca(tipo_conteudo, r'CÂMARA') == 'has': #caso contenha camera seja referente a camera ignora
            continue
        else:
            texto = str(nota['texto'])
            if verifica_resultado_busca(texto, r'Audiência Pública') == 'has': #se realmente tiver audiencia publica armazena obejto em um dicionario cuja a posicao e o id
                id_obj = nota['id']
                index = retorna_indice(id_obj)
                audiencias[index] = nota


    for teste in   audiencias:
        #inseri link da lista de audienciaes selecionadas
        links[teste] = "http://devcolab.each.usp.br/do/"+audiencias[teste]['id']
        #texto da repectiva audiencia
        texto = str(audiencias[teste]['texto'])
        #pegar todos os formatos de datas e armazena em data teste
        datas[teste] = [re.findall(r'\d{1,2}\/\d{1,2}\/\d{2,4}', texto)]+[re.findall(r'\d{1,2}\s\w+\s\w+\s\w+\s\d{2,4}' , texto)]
        datas[teste] = filtra_data(datas[teste])    #possiveis datas caso nao exista datas posiveis o conteudo e None
        
    for audiencia in audiencias:
        if not datas[audiencia]: #caso o for acima nao pegou nenhuma data para essa audiencia
            objt = {'title' : audiencias[audiencia]['secretaria'], 'date': None, 'url': links[audiencia] }
        else:
            data = str(datas[audiencia][0])
            objt = {'title' : audiencias[audiencia]['secretaria'], 'date': data, 'url': links[audiencia] }
            sys.stdout.writelines(objt)
            

if __name__ == '__main__':
    main()
    





        
        
