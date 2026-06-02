# ARL-PRO (资产侦察灯塔系统进阶版)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Vue](https://img.shields.io/badge/Vue.js-3.x-4FC08D.svg)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)
![Build](https://img.shields.io/github/actions/workflow/status/owl234/arl-pro/deploy-laptop.yml?label=CI%2FCD)

ARL-PRO 是对原版 ARL（Asset Reconnaissance Lighthouse）的全面重构与进阶版本，旨在提供更加现代化、高并发和高度自动化的资产侦察与漏洞扫描功能。系统采用前后端完全分离架构，内置丰富的 ARL-NPoC 武器库、GitHub 敏感信息监控模块，并打通了 GitHub Actions 自动化 CI/CD 部署流水线，为安全研究人员提供持续、稳定的 0-day 挖掘与资产监控能力。

---

## 1. 整体功能和架构梳理

系统采用微服务化的容器编排设计，根据 `docker-compose` 的配置，整个系统主要由以下核心服务构成：

* **前端服务 (frontend)**：基于 **Vue 3** 和 **Vite** 构建。提供现代化的单页面应用 (SPA) 界面，运行在 Nginx 容器中。
* **后端 Web API 服务 (backend)**：基于 **Python**、**Flask** 和 **Flask-RESTX** 开发。提供 RESTful API，处理用户请求、数据查询和任务调度，通过 Gunicorn 运行。
* **核心扫描节点 (worker)**：基于 **Celery** 的分布式工作节点，负责执行重量级的资产收集和扫描任务（如域名枚举、端口扫描、漏洞探测等）。
* **GitHub 监控节点 (worker-github)**：专门用于监控 GitHub 源码泄露和敏感信息的独立 Celery 节点。
* **定时调度器 (scheduler)**：处理周期性任务和计划任务的分布式调度模块。
* **消息队列 (rabbitmq)**：作为 Celery 的 Broker，负责后端 API、Scheduler 与各个 Worker 之间的任务消息传递。
* **数据库引擎 (mongodb)**：存储各种扫描结果、资产数据、指纹信息及任务状态等持久化数据。

## 2. 技术栈总结

* **前端生态**：Vue 3, Vite, Ant Design Vue, Vue Router, Axios
* **后端生态**：Python 3, Flask, Flask-RESTX, Gunicorn
* **分布式/高并发**：Celery, RabbitMQ
* **持久化存储**：MongoDB
* **DevOps/部署**：Docker, Docker Compose, GitHub Actions, Shell 自动化

---

## 3. 🚀 部署方式一：生产环境 CI/CD 自动部署 (强烈推荐)

本系统全面打通了 CI/CD 自动化流水线。只需在一台纯净的 Ubuntu 服务器/虚拟机上执行以下三步，后续的所有构建、运行与端口放行均由流水线接管。

> **⚠️ 开发者必看（流水线配置更新）**：
> 由于我们为生产环境启用了更规范的 `docker-compose.test.yml`（直接映射宿主机 80 端口），请确保你的 `.github/workflows/deploy-laptop.yml` 文件中，执行的是 `test.yml`，例如：
> `docker compose -f docker-compose.test.yml up -d --build`

### Step 1: 节点环境一键初始化
拉取代码后，在你的 Ubuntu 终端执行以下脚本：
```bash
# 赋予执行权限并运行
chmod +x init_ubuntu_env.sh
./init_ubuntu_env.sh
```
> **⚙️ 脚本会自动完成以下基建：**
> 1. 下载并安装最新版 Docker Engine。
> 2. 将当前用户加入 `docker` 组（实现 Docker 免 `sudo` 执行）。
> 3. 自动配置 `/etc/sudoers.d/` 提权规则，赋予流水线免密执行 `ufw` 防火墙放行的特权。

### Step 2: 配置并注册 GitHub Runner
为了接收 GitHub 下发的自动化部署任务，需要在本节点安装并常驻运行 Runner 服务：
1. 打开本项目 GitHub 网页：`Settings` -> `Actions` -> `Runners` -> `New self-hosted runner`。
2. 按照网页提示下载 Runner 程序。执行配置命令绑定仓库：
   ```bash
   ./config.sh --url https://github.com/owl234/arl-pro --token <你的网页Token>
   ```
   *注意：提示 `Enter any additional labels` 时，请输入与你流水线匹配的标签（如 `laptop`）。*
3. 将 Runner 安装为后台常驻服务并启动：
   ```bash
   sudo ./svc.sh install
   sudo ./svc.sh start
   ```

### Step 3: 刷新权限与触发部署
如果是首次配置，需要刷新用户组权限以让 Docker 免密生效：
```bash
# 刷新权限并重启 Runner 服务
newgrp docker
cd actions-runner
sudo ./svc.sh stop && sudo ./svc.sh start
```
**完成！** 现在只需向 `main` 分支推送代码，流水线将自动拉起所有分布式容器，并**自动放行前端 (80) 和后端 API (5003) 端口**。

---

## 4. 💻 部署方式二：测试与本地环境手动部署

如果您希望在本地（如 Windows/Mac）修改代码进行调试，或不希望使用 CI/CD 流水线，请确保本地已安装 Docker 和 Docker Compose (v2)。

```bash
# 1. 克隆代码
git clone https://github.com/owl234/arl-pro.git
cd arl-pro

# ===================================================
# 方式 A: 测试/生产环境手动部署 (映射宿主机 80 端口)
# 推荐用于直接提供服务的测试机，使用预编译配置。
# ===================================================
docker compose -f docker-compose.test.yml up -d

# ===================================================
# 方式 B: 本地开发/沙盒环境 (映射宿主机 8080 端口)
# 推荐用于基于本地源代码实时挂载运行、二次开发。
# ===================================================
docker compose -f docker-compose.local.yml up -d --build
```

### 🔑 默认账号密码与登录

无论采用哪种方式启动，等所有容器（frontend, backend, worker, mongodb, rabbitmq 等）处于 `running` 状态后，可通过浏览器访问系统：

* **访问地址**：
    * 生产/测试模式（CI/CD 或 test.yml）：`http://您的服务器IP/`
    * 本地开发模式（local.yml）：`http://127.0.0.1:8080/`
* **默认登录账号**：`admin`
* **默认登录密码**：`arlpass`

> **🛡️ 安全提示**：登录后，请务必前往个人设置中心修改默认密码，保证资产系统的安全。

---

## 5. 完成度评估 (功能清单)

目前项目已经实现了核心功能模块的重构，完成度极高：

### 5.1 前端功能模块
* **系统与基础界面**：登录 (Login)、布局 (Layout)。
* **任务管理**：任务列表 (TaskList)、任务详情 (TaskDetail)、计划任务 (PlanningTasks)。
* **资产管理**：资产搜索、资产监控、资产范围、指纹信息、资产组详情。
* **漏洞与策略管理**：PoC 管理 (PocList)、策略管理 (Policy)、策略详情 (PolicyDetail)。
* **GitHub 监控**：GitHub 任务列表、任务信息、监控列表、监控信息。

### 5.2 后端 API 支持
提供了丰富的 API 接口，全面支撑前端和扫描引擎：
* **资产类**：`domain`, `ip`, `site`, `url`, `image`, `cert`, `service`, `fileleak`, `wih`, `cip` 等。
* **任务与调度类**：`task`, `scheduler`, `task_schedule`, `task_fofa` 等。
* **漏洞与安全类**：`poc`, `vuln`, `policy`, `npoc_service`, `fingerprint`, `nuclei_result` 等。
* **GitHub 监控类**：`github_task`, `github_result`, `github_scheduler`, `github_monitor_result` 等。

## 6. 近期开发动态

* **DevOps 升级**：全面打通 GitHub Actions 自动化部署流水线，支持 Ubuntu 节点一键环境装配与免密提权。
* **容灾与高可用配置**：为所有核心组件开启开机自启 (`restart: always`)。确保前端、后端、各个工作节点、数据库和消息队列在异常退出或宿主机重启后能够自动恢复，大幅提升系统的可靠性和无人值守能力。