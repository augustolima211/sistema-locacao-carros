# 🚀 Instruções de Deploy - Streamlit Cloud

## 📋 Pré-requisitos

✅ **Arquivos Essenciais Incluídos:**
- `locauto.py` - Aplicação principal
- `requirements.txt` - Dependências
- `logo.png` - Logo da empresa
- `*.csv` - Dados iniciais
- `ultima_fatura.txt` - Controle de numeração
- `README.md` - Documentação
- `.gitignore` - Arquivos ignorados
- `.streamlit/config.toml` - Configurações do tema

## 🔧 Passos para Deploy

### 1. Preparar Repositório GitHub

```bash
# Inicializar repositório
git init
git add .
git commit -m "Sistema de Locação de Carros - Deploy Streamlit Cloud"

# Conectar ao GitHub
git branch -M main
git remote add origin https://github.com/augustiloma211/sistema-locacao-carros.git
git push -u origin main
```

### 2. Configurar no Streamlit Cloud

1. Acesse [share.streamlit.io](https://share.streamlit.io)
2. Faça login com sua conta GitHub
3. Clique em **"New app"**
4. Configure:
   - **Repository:** `augustiloma211/sistema-locacao-carros`
   - **Branch:** `main`
   - **Main file path:** `locauto.py`
   - **App URL:** `sistema-locacao-carros` (ou personalizado)

### 3. Configurações Avançadas (Opcional)

**Python Version:** 3.9+ (recomendado)  
**Advanced settings:** Deixar padrão

## ✅ Verificações Pós-Deploy

- [ ] App carrega sem erros
- [ ] Todas as páginas funcionam
- [ ] Geração de PDF funciona
- [ ] Upload/download de dados funciona
- [ ] Gráficos são exibidos corretamente

## 🔗 URLs de Acesso

Após o deploy, seu app estará disponível em:  
`https://augustiloma211-sistema-locacao-carros-main-HASH.streamlit.app`

## 🛠️ Solução de Problemas

**Erro de Dependências:**
- Verifique se todas as dependências estão no `requirements.txt`
- Use versões específicas se necessário

**Erro de Arquivos:**
- Certifique-se que todos os arquivos CSV estão no repositório
- Verifique se o `logo.png` foi incluído

**Performance:**
- O Streamlit Cloud tem recursos limitados no plano gratuito
- Para uso intensivo, considere upgrade para plano pago

## 📞 Suporte

Em caso de problemas, consulte:
- [Documentação Streamlit Cloud](https://docs.streamlit.io/streamlit-cloud)
- [Community Forum](https://discuss.streamlit.io/)