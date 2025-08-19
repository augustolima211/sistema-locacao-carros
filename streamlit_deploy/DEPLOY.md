# 🚀 Guia de Deploy - Streamlit Cloud

## ⚠️ PROBLEMA IDENTIFICADO E SOLUÇÃO

### 🔍 **Problema:**
O dashboard mostra zeros (0 clientes, 0 veículos, R$ 0,00) no Streamlit Cloud, mesmo com dados no código.

### ✅ **Solução Implementada:**

1. **Importação Automática de Dados**
   - O sistema agora verifica automaticamente se há dados no banco
   - Se estiver vazio, executa a importação dos dados de backup
   - Dados são carregados na primeira inicialização

2. **Dados de Backup Integrados**
   - 10 veículos pré-cadastrados
   - 4 clientes pré-cadastrados
   - Dados hardcoded no arquivo `import_backup.py`

## 📋 **Passos para Deploy Correto:**

### 1. **Preparação dos Arquivos**
```
streamlit_deploy/
├── locauto.py              # ✅ Aplicação principal (MODIFICADO)
├── database_manager.py     # ✅ Gerenciador de banco
├── import_backup.py        # ✅ Importação automática
├── setup.py               # ✅ Configuração inicial
├── requirements.txt        # ✅ Dependências
├── README.md              # ✅ Documentação
└── DEPLOY.md              # ✅ Este arquivo
```

### 2. **Upload para GitHub**
- Faça upload de TODA a pasta `streamlit_deploy`
- Certifique-se que todos os arquivos estão incluídos
- **IMPORTANTE:** O arquivo `import_backup.py` é essencial!

### 3. **Configuração no Streamlit Cloud**
- Repository: Seu repositório GitHub
- Branch: main (ou master)
- Main file path: `locauto.py`
- Python version: 3.9+ (recomendado)

### 4. **Primeira Execução**
- ⏱️ **Aguarde 1-2 minutos** após o deploy
- O sistema executará automaticamente:
  1. Criação do banco de dados
  2. Verificação de dados existentes
  3. Importação automática se necessário
  4. Exibição das métricas

## 🔧 **Verificação de Funcionamento:**

### ✅ **Sinais de Sucesso:**
- Dashboard mostra: 4 clientes, 10 veículos
- Receita total > R$ 0,00
- Listas de clientes e veículos populadas
- Mensagem: "✅ Dados de backup importados com sucesso!"

### ❌ **Se Ainda Mostrar Zeros:**
1. **Recarregue a página** (F5)
2. **Aguarde mais 30 segundos**
3. **Verifique os logs** do Streamlit Cloud
4. **Procure por erros** na importação

## 📊 **Dados Esperados Após Deploy:**

### 🚗 **Veículos (10 total):**
- ARGO - QPQ3E24 (2019) - BRANCO - R$ 80,00
- ARGO - RVV9I66 (2023) - BRANCO - R$ 80,00
- FORD K - FSS5E24 (2018) - BRANCO - R$ 70,00
- HB20 - FVN0F16 (2019) - PRETO - R$ 80,00
- LOGAN - GFY4C68 (2021) - BRANCO - R$ 80,00
- MOBI - QWR7J17 (2020) - BRANCO - R$ 80,00
- NOVO UNO - RFL4J94 (2020) - BRANCO - R$ 80,00
- ONIX LT - QQA0J66 (2019) - BRANCO - R$ 80,00
- SPIN - EWU1I34 (2013) - BRANCO - R$ 80,00
- FOD K - GDH8111 (2018) - BRANCO - R$ 80,00

### 👥 **Clientes (4 total):**
- ALINE DE OLIVEIRA MORAIS MOREURA - 312.584.818-04
- CELSO ANTONIO DE MELO - 011.776.116-86
- NAILTON BISPO DE ROMA - 098.422.466-12
- lago cunha soluções agricolas ltda - 57.334.181/0001-00

## 🚨 **Troubleshooting:**

### **Problema: Dados não aparecem**
**Solução:**
1. Verifique se `import_backup.py` está no repositório
2. Recarregue a aplicação
3. Aguarde a importação automática

### **Problema: Erro de importação**
**Solução:**
1. Verifique os logs do Streamlit Cloud
2. Confirme que todas as dependências estão instaladas
3. Redeploye a aplicação

### **Problema: Cache antigo**
**Solução:**
1. Limpe o cache do navegador
2. Use modo incógnito
3. Aguarde alguns minutos

---

## ✅ **Checklist Final:**

- [ ] Todos os arquivos estão no GitHub
- [ ] `import_backup.py` está incluído
- [ ] Deploy realizado no Streamlit Cloud
- [ ] Aguardou 1-2 minutos após deploy
- [ ] Dashboard mostra dados corretos
- [ ] Sistema funcionando 100%

**🎉 Com essas modificações, o sistema funcionará perfeitamente no Streamlit Cloud!**