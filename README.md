# DevOps Project: Infrastructure, Monitoring & Logging Automation

## Project Architecture
1.  **CI (GitHub Actions):** Lints and tests the Python FastAPI backend on every push.
2.  **IaC (Terraform):** Provisions a t3.micro Ubuntu 24.04 instance on AWS with automated AMI discovery.
3.  **Configuration (Ansible):** Automatically configures Nginx, Prometheus, and Filebeat once the hardware is ready.
4.  **Observability:** Prometheus tracks system metrics while Filebeat captures application logs.


---

## Quick Start Setup

### 1. Prerequisites
* An **AWS Account** with an IAM user (Access/Secret keys).
* A **GitHub Repository** for this code.
* An **SSH Key Pair** created in the AWS Console (London `eu-west-2`) named: `assignment-final-key`.

### 2. GitHub Secrets Configuration
Navigate to **Settings > Secrets and variables > Actions** and add the following secrets:

| Secret Name | Value/Description |
| :--- | :--- |
| `AWS_ACCESS_KEY_ID` | Your AWS Access Key |
| `AWS_SECRET_ACCESS_KEY` | Your AWS Secret Key |
| `AWS_REGION` | `eu-west-2` or Your Preferred Region|
| `SSH_PRIVATE_KEY` | The full text of your `.pem` private key file |

### 3. Deployment
Push your code to the `main` branch. GitHub Actions will:
* Run Python unit tests.
* Provision the EC2 instance.
* Deploy the web app and monitoring suite via Ansible.

---

## Verification

After a successful run, use the **Public IP** from the GitHub Action output to verify:

### Web Server
* **Access:** `http://<YOUR_IP>`
* **Expected:** "Task 2 & 3 Complete: Infrastructure Automation + Monitoring + Logging".

### Monitoring (Prometheus)
* **Dashboard:** `http://<YOUR_IP>:9090`
* **Alerts:** Check `http://<YOUR_IP>:9090/alerts` to see the **InstanceDown** rule.



### Logging (Filebeat)
* [cite_start]**Method:** This setup uses a lightweight **Filebeat** agent to avoid RAM exhaustion[cite: 40].
* **Verification:** View the **"Verify Nginx Logging"** step in your GitHub Action logs. It will show real-time JSON log entries captured from Nginx.

---

## Design Decisions & Troubleshooting (Assumptions & Challenges)
* **AWS User Type:** Switched to ubuntu instead of Amazon Linux Service 2023 due to problems recognising SSH Keys with older RSA signatures that are often used in Github Runners.
* **OS:** Assumed Debian-based environment(Ubuntu) would be better than Amazon Linux due to wider support and native .deb package compatability for Prometheus and Filebeat
* [cite_start]**Resource Constraints:** To ensure stability on a `t3.micro` (1GB RAM), I opted for **Filebeat** local logging instead of a full ELK stack, which requires ~4GB RAM[cite: 40].
* **Infrastructure Idempotency:** The CI/CD pipeline includes logic to **Import** existing Security Groups. This allows you to re-run the pipeline multiple times without "Resource Already Exists" errors.
* **Networking:** Assumed single-node deployment as project is very small, thus Load-Balancer is not provisioned and app is accessed directly by the EC2 Public IP.
* **Security:** For demonstration purposes, ingress rules for ports are set to 0.0.0.0/0 - In a production Environment, this would be restricted.
* **Terraform State Conflicts:** Due to Github Actions starting fresh every time, there is no terraform.tfstate file, causing Terraform to try to create a the same security group on every pipeline run, leading to an AlreadyExists error. Solved by using name_prefix in main.tf, allowing unique resource naming as well as addition of pre-apply script in deploy.yml that uses AWS CLI to check if the security group alreay exists or not.
* **Prometheus Status 2 Exit Code:** Prometheus sometimes failed to start due to no clearly defined Working Directory to write it's Time Series Database. Solved by modifying anisble playbook to include creation of /data directory with ubuntu permissions, adding the Working Directory to the prometheus.service template.

--

## Potential Performance Issues & How to deal with
* **High Response Times (Latency):** Check Promteheus node_cpu_seconds_total "steal" time - If CPU is constantly at 100%, update main.tf file with changing instance_type to t3.small or t3.medium. Also ensure heavy Input/Output tasks use await.
* **Frequent Errors:** This would be due to a breakdown between components, e.g. 502 Bad Gateway when the backend has crashed/is not listening properly whilst Nginx is running or 504 Gateway Timeout where the backend is taking too long to respond or 429 Too Many Requests where the server is gettng more requests than the Python Worker can handle. To identify and deal with these, you can check the filebeat output or raw logs. Preventative measures can include ensuring the backend is managed by systemd with Restart=always so if it does crash, it should automatically recover.
* **Resource Saturation:** As I am using a small EC2 instance (t3.micro), resources can be filled very quickly, with Python processes,Prometheus metrics or Nginx logs growing quickly. To handle this, I would set up alerts in Prometheus looking at remaining available memory to warn of when this is happening and to handle the problem appropriately depending on the situation (much like Kubernetes would).

---

## Repository Structure
* `.github/workflows/`: CI/CD Pipeline definitions.
* `ansible/`: Playbooks for server configuration.
* `backend/`: Python FastAPI source code and tests.
* `frontend/`: Simple React+Vite frontend.
* `terraform/`: AWS Infrastructure-as-Code.

---

## Cleanup
To prevent ongoing AWS charges, terminate the instance via the AWS Console or run:
```bash
terraform destroy
