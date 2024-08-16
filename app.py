import yfinance as yf
import streamlit as st  
import pandas as pd

nova_acao = st.text_input("Digite o codigo de uma acao: ", key="nova_acao")

#funcao de carregamento dos dados
def carregar_dados(empresas):
    texto_tickers = " ".join(empresas)
    dados_acao = yf.Tickers(texto_tickers)
    cotacoes_acao = dados_acao.history(start= "2020-01-01", end= "2024-01-01", interval = "1mo")
    cotacoes_acao = cotacoes_acao["Open"]
    return cotacoes_acao
    
acoes = ["ITUB4.SA", "PETR4.SA", "MGLU3.SA", "VALE3.SA" , nova_acao]   
dados = carregar_dados(acoes) 

#sidebar
st.sidebar.header("Filtros")


#filtros
lista_acoes = st.sidebar.multiselect("Escolha as acoes para visualizar", dados.columns)
if lista_acoes:
    dados = dados[lista_acoes]
    if len(lista_acoes) == 1:
        acao_unica = lista_acoes[0]
        dados = dados.rename(columns={acao_unica: "Open"})
    
#filtro de data
data_inicial = dados.index.min().to_pydatetime()
data_final = dados.index.max().to_pydatetime()
intervalo_data = st.sidebar.slider("Selecione o perido", min_value = data_inicial, max_value = data_final, value=(data_inicial,data_final)) 
dados = dados.loc[intervalo_data[0]:intervalo_data[1]]

#texto no streamlit
st.write(f"""
### App precos de Acoes
O Grafico abaixo representa a evolucao o preco das acoes {lista_acoes} com inicio em {intervalo_data[0].strftime("%d/%m/%Y")} 
e final em {intervalo_data[1].strftime("%d/%m/%Y")}.
""")
        
#Criacao do grafico
st.line_chart(dados)

#performance dos ativos
texto_performance_ativos = ""

if len(lista_acoes) == 0:
    lista_acoes = list(dados.columns)
elif len(lista_acoes) == 1:
    dados = dados.rename(columns={"Open": acao_unica}) 
    
    
carteira = [1000 for acao in lista_acoes]
total_inicial_carteira = sum(carteira)    
    
for i, acao in enumerate(lista_acoes):
    performance_ativo = dados[acao].iloc[-1]/dados[acao].iloc[0] - 1
    performance_ativo = float(performance_ativo)
    
    carteira[i] = carteira[i] * (1 + performance_ativo)
    
    if performance_ativo > 0:
        texto_performance_ativos = texto_performance_ativos + f"  \n{acao}:  :green[{performance_ativo:.2%}]"
    elif performance_ativo < 0:
        texto_performance_ativos = texto_performance_ativos + f"  \n{acao}:  :red[{performance_ativo:.2%}]"
    else:
        texto_performance_ativos = texto_performance_ativos + f"  \n{acao}:  {performance_ativo:.2%}"        

total_final_carteira = sum(carteira) 
performance_carteira = total_final_carteira/total_inicial_carteira - 1

if performance_carteira > 0:
    texto_performance_carteira = f"Performance da carteira com todos os ativos : :green[{performance_carteira:.2%}]"
elif performance_carteira < 0:
    texto_performance_carteira = f"Performance da carteira com todos os ativos : :red[{performance_carteira:.2%}]"
else:
    performance_carteira = f"Performance da carteira com todos os ativos :  {performance_carteira:.2%}"   

#texto no streamlit
st.write(f"""
### Performance dos ativos
Essa foi a performance de cada ativo no periodo de {intervalo_data[0].strftime("%d/%m/%Y")} a {intervalo_data[1].strftime("%d/%m/%Y")}.

{texto_performance_ativos}

{texto_performance_carteira}

""")