import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Configurando o título do app
st.title("Análise RFV - Segmentação de Clientes")

# Upload do arquivo CSV
uploaded_file = st.file_uploader("Envie o arquivo de dados (.csv)", type="csv")
if uploaded_file:
    # Carregando os dados
    df_compras = pd.read_csv(uploaded_file, infer_datetime_format=True, parse_dates=['DiaCompra'])
    st.write("### Visualizando os primeiros dados:")
    st.dataframe(df_compras.head(20))
    
    # Informações básicas
    st.write("### Informações da Tabela")
    st.write(f"**Número de Linhas e Colunas:** {df_compras.shape}")
    st.write(f"**Data mínima de compra:** {df_compras['DiaCompra'].min()}")
    st.write(f"**Data máxima de compra:** {df_compras['DiaCompra'].max()}")
    
    # Configurando a data atual
    dia_atual = datetime(2021, 12, 9)
    
    # Cálculo de Recência
    st.write("## Analisando Recência")
    df_recencia = df_compras.groupby(by='ID_cliente', as_index=False)['DiaCompra'].max()
    df_recencia.columns = ['ID_cliente', 'DiaUltimaCompra']
    df_recencia['Recencia'] = df_recencia['DiaUltimaCompra'].apply(lambda x: (dia_atual - x).days)
    df_recencia.drop('DiaUltimaCompra', axis=1, inplace=True)
    st.dataframe(df_recencia.head())
    
    # Frequência
    st.write("## Analisando Frequência")
    df_frequencia = df_compras[['ID_cliente', 'CodigoCompra']].groupby('ID_cliente').count().reset_index()
    df_frequencia.columns = ['ID_cliente', 'Frequencia']
    st.dataframe(df_frequencia.head())
    
    # Valor
    st.write("## Analisando Valor")
    df_valor = df_compras[['ID_cliente', 'ValorTotal']].groupby('ID_cliente').sum().reset_index()
    df_valor.columns = ['ID_cliente', 'Valor']
    st.dataframe(df_valor.head())
    
    # Criando tabela RFV
    st.write("## Criando Tabela RFV")
    df_RF = df_recencia.merge(df_frequencia, on='ID_cliente')
    df_RFV = df_RF.merge(df_valor, on='ID_cliente')
    df_RFV.set_index('ID_cliente', inplace=True)
    st.dataframe(df_RFV.head())
    
    # Quartis
    st.write("## Definindo Quartis")
    quartis = df_RFV.quantile(q=[0.25, 0.5, 0.75])
    st.write("### Quartis Calculados:")
    st.write(quartis)
    
    # Funções para classificação
    def recencia_class(x, r, q_dict):
        if x <= q_dict[r][0.25]:
            return 'A'
        elif x <= q_dict[r][0.50]:
            return 'B'
        elif x <= q_dict[r][0.75]:
            return 'C'
        else:
            return 'D'
    
    def freq_val_class(x, fv, q_dict):
        if x <= q_dict[fv][0.25]:
            return 'D'
        elif x <= q_dict[fv][0.50]:
            return 'C'
        elif x <= q_dict[fv][0.75]:
            return 'B'
        else:
            return 'A'
    
    # Aplicando as classificações
    df_RFV['R_quartil'] = df_RFV['Recencia'].apply(recencia_class, args=('Recencia', quartis))
    df_RFV['F_quartil'] = df_RFV['Frequencia'].apply(freq_val_class, args=('Frequencia', quartis))
    df_RFV['V_quartil'] = df_RFV['Valor'].apply(freq_val_class, args=('Valor', quartis))
    df_RFV['RFV_Score'] = df_RFV.R_quartil + df_RFV.F_quartil + df_RFV.V_quartil
    
    st.write("### Tabela RFV com Classificação:")
    st.dataframe(df_RFV.head())
    
    # Ações de marketing/CRM
    dict_acoes = {
        'AAA': 'Enviar cupons de desconto, pedir indicações, enviar amostras grátis.',
        'DDD': 'Clientes de baixo valor e pouca frequência, não fazer nada.',
        'DAA': 'Clientes que gastaram bastante, enviar cupons para recuperar.',
        'CAA': 'Clientes importantes, enviar incentivos para fidelização.'
    }
    df_RFV['acoes de marketing/crm'] = df_RFV['RFV_Score'].map(dict_acoes)
    
    st.write("### Tabela RFV com Ações de Marketing:")
    st.dataframe(df_RFV.head())
    
    # Exportar para Excel
    st.write("## Exportar Resultados")
    if st.button("Exportar para Excel"):
        df_RFV.to_excel('./RFV_Segmentacao.xlsx')
        st.success("Arquivo exportado como 'RFV_Segmentacao.xlsx'")
