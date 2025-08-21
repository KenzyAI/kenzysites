# 🚀 Guia de Migração - KenzySites

## 📦 Backup Completo Criado

### Arquivos de Backup Gerados:

1. **`backup/postgres_dump.sql`** - Dump SQL completo do banco PostgreSQL
2. **`backup/volumes/postgres_data_backup.tar.gz`** - Backup completo do volume PostgreSQL
3. **`backup/volumes/redis_data_backup.tar.gz`** - Backup completo do volume Redis

---

## 🔄 Como Migrar para Outro PC

### 1. **Preparar o Novo PC**

```bash
# Instalar Docker e Docker Compose
# Ubuntu/Debian:
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. **Transferir Arquivos**

#### Opção A: Usando Git + Backup Manual
```bash
# No PC atual
tar czf kenzysites-complete-backup.tar.gz . backup/

# Transferir via:
# - Google Drive, Dropbox, OneDrive
# - Pendrive/HD Externo
# - SSH/SCP: scp kenzysites-complete-backup.tar.gz user@novo-pc:/caminho/
```

#### Opção B: Usando Git Repository
```bash
# 1. Criar repositório no GitHub
# 2. Push do código (já feito)
# 3. No novo PC:
git clone https://github.com/SEU_USUARIO/kenzysites.git
cd kenzysites

# 4. Transferir apenas backup/
scp -r backup/ user@novo-pc:/caminho/kenzysites/
```

### 3. **Restaurar no Novo PC**

```bash
# 1. Entrar no diretório do projeto
cd kenzysites

# 2. Iniciar containers (irá criar volumes vazios)
docker-compose up -d

# 3. Parar containers para restaurar dados
docker-compose down

# 4. Restaurar volumes PostgreSQL
docker run --rm -v kenzysites_postgres_data:/target -v $(pwd)/backup/volumes:/backup alpine:latest sh -c "cd /target && tar xzf /backup/postgres_data_backup.tar.gz"

# 5. Restaurar volumes Redis
docker run --rm -v kenzysites_redis_data:/target -v $(pwd)/backup/volumes:/backup alpine:latest sh -c "cd /target && tar xzf /backup/redis_data_backup.tar.gz"

# 6. Reiniciar containers
docker-compose up -d

# 7. Aguardar containers iniciarem (30 segundos)
sleep 30

# 8. Verificar se banco foi restaurado
docker exec kenzysites-db-1 psql -U postgres -l
```

### 4. **Verificação Pós-Migração**

```bash
# Verificar containers ativos
docker ps

# Verificar logs
docker-compose logs

# Testar acesso ao banco
docker exec -it kenzysites-db-1 psql -U postgres -d wordpress_ai_builder

# Verificar aplicação
curl http://localhost:8000/health
curl http://localhost:3000
```

---

## 🛠️ Restauração Alternativa (Usando SQL Dump)

Se a restauração por volumes não funcionar:

```bash
# 1. Iniciar apenas PostgreSQL
docker-compose up -d db

# 2. Aguardar inicialização
sleep 30

# 3. Criar banco
docker exec kenzysites-db-1 createdb -U postgres wordpress_ai_builder

# 4. Restaurar dump SQL
docker exec -i kenzysites-db-1 psql -U postgres wordpress_ai_builder < backup/postgres_dump.sql

# 5. Iniciar todos os serviços
docker-compose up -d
```

---

## 📋 Checklist de Migração

### Antes de Migrar:
- [ ] ✅ Backup completo criado
- [ ] ✅ Código commitado no Git
- [ ] [ ] Repository remoto configurado (GitHub/GitLab)
- [ ] [ ] Teste dos backups (opcional)

### No Novo PC:
- [ ] Docker e Docker Compose instalados
- [ ] Projeto clonado/transferido
- [ ] Backup transferido
- [ ] Volumes restaurados
- [ ] Containers iniciados
- [ ] Aplicação testada

---

## 🚨 Troubleshooting

### Problema: Containers não iniciam
```bash
# Verificar logs
docker-compose logs

# Limpar volumes (CUIDADO: perde dados)
docker-compose down -v
docker volume prune
```

### Problema: Banco não funciona
```bash
# Verificar se banco existe
docker exec kenzysites-db-1 psql -U postgres -l

# Restaurar usando SQL dump
docker exec -i kenzysites-db-1 psql -U postgres wordpress_ai_builder < backup/postgres_dump.sql
```

### Problema: Permissões
```bash
# Ajustar permissões (Linux)
sudo chown -R $USER:$USER .
chmod -R 755 .
```

---

## 📊 Tamanhos dos Backups

- **PostgreSQL Volume**: ~8.5 MB
- **Redis Volume**: ~92 bytes  
- **SQL Dump**: ~16 KB
- **Total**: ~8.6 MB

---

## 🔗 Links Úteis

- [Docker Install](https://docs.docker.com/get-docker/)
- [Docker Compose Install](https://docs.docker.com/compose/install/)
- [Git Documentation](https://git-scm.com/doc)

---

**✅ Migração Preparada com Sucesso!**

Todos os dados estão seguros no diretório `backup/`. Siga este guia para migrar sem perder nenhuma informação.