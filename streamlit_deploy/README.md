# 🚗 LocAuto - Sistema de Locação de Veículos

## 📋 Sobre o Sistema

Sistema completo de gestão de locação de veículos com:
- Dashboard executivo com métricas
- Gestão de clientes e veículos
- Emissão de faturas em PDF
- Controle financeiro
- Relatórios e análises

## 🚀 Deploy no Streamlit Cloud

### ⚠️ IMPORTANTE - Dados de Backup

O sistema possui dados de backup integrados que são importados automaticamente quando:
1. O banco de dados está vazio
2. Não há clientes ou veículos cadastrados

### 📊 Dados Incluídos no Backup:

**🚗 Veículos (10 unidades):**
- ARGO - QPQ3E24 (2019) - BRANCO - R$ 80,00
- ARGO - RVV9I66 (2023) - BRANCO - R$ 80,00
- FORD K - FSS5E24 (2018) - BRANCO - R$ 70,00
- HB20 - FVN0F16 (2019) - PRETO - R$ 80,00
- LOGAN - GFY4C68 (2021) - BRANCO - R$ 80,00
- E mais 5 veículos...

**👥 Clientes (4 unidades):**
- ALINE DE OLIVEIRA MORAIS MOREURA - 312.584.818-04
- CELSO ANTONIO DE MELO - 011.776.116-86
- NAILTON BISPO DE ROMA - 098.422.466-12
- lago cunha soluções agricolas ltda - 57.334.181/0001-00

### 🔧 Solução para Dados Não Aparecendo

Se o dashboard mostrar zeros após o deploy:

1. **Aguarde 30-60 segundos** - O sistema importa dados automaticamente
2. **Recarregue a página** (F5 ou Ctrl+R)
3. **Limpe o cache do navegador** se necessário
4. **Verifique os logs** do Streamlit Cloud para mensagens de importação

### 📁 Arquivos Importantes

- `locauto.py` - Aplicação principal
- `database_manager.py` - Gerenciador do banco de dados
- `import_backup.py` - Script de importação automática
- `setup.py` - Configuração inicial
- `requirements.txt` - Dependências Python

### 🛠️ Dependências

```
streamlit>=1.39.0
pandas>=2.1.0
plotly>=5.18.0
xhtml2pdf>=0.2.11
typing-extensions>=4.9.0
```

### 🎯 Funcionalidades

- ✅ Dashboard com métricas em tempo real
- ✅ Cadastro completo de clientes e veículos
- ✅ Geração de faturas em PDF profissionais
- ✅ Controle financeiro com receitas e despesas
- ✅ Relatórios e gráficos interativos
- ✅ Backup automático de dados
- ✅ Interface moderna e responsiva

### 📞 Suporte

Se os dados não aparecerem após 2 minutos:
1. Verifique os logs do Streamlit Cloud
2. Procure por mensagens de "Importando dados de backup"
3. Recarregue a aplicação

---

**🎉 Sistema pronto para uso com dados de demonstração incluídos!**