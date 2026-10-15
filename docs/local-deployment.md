# 🐳 ClinicPulse — Local Deployment Guide

This beginner-friendly guide explains how to deploy ClinicPulse locally using Docker.

You do not need previous DevOps experience.

## 1. What Is ClinicPulse?

ClinicPulse is a healthcare service monitoring and incident simulation application.

It provides:

- Appointment service monitoring
- Pharmacy service monitoring
- Laboratory service monitoring
- Service failure simulation
- Incident recovery
- AI-assisted incident investigation using Amazon Bedrock
- A web-based monitoring dashboard

The three healthcare services are simulated endpoints within one Flask application.

## 2. Prerequisites

You need:

- Ubuntu 22.04 or 24.04
- Internet connection
- Terminal access
- Sudo privileges
- Approximately 2 GB of free disk space

We will install Git and Docker.

## 3. Install Git

Update the package list:

```bash
sudo apt update
```

Install Git:

```bash
sudo apt install git -y
```

Verify installation:

```bash
git --version
```

Git allows us to download the ClinicPulse source code from GitHub.

## 4. Install Docker

Install Docker:

```bash
sudo apt install docker.io -y
```

Start Docker:

```bash
sudo systemctl start docker
```

Enable Docker at startup:

```bash
sudo systemctl enable docker
```

Verify Docker:

```bash
sudo docker --version
```

Check Docker service:

```bash
sudo systemctl status docker
```

The service should show `active (running)`.

## 5. Clone ClinicPulse

Download the project:

```bash
git clone https://github.com/akhilantotharayil/clinicpulse.git
```

Enter the project directory:

```bash
cd clinicpulse
```

View project files:

```bash
ls -la
```

You should see files including:

- Dockerfile
- requirements.txt
- start.sh
- app/
- templates/
- static/
- tests/

## 6. Understand the Dockerfile

ClinicPulse uses a multi-stage Dockerfile.

Stage 1 installs Python dependencies.

Stage 2 creates the runtime image.

The application:

- Uses Python and Flask
- Runs through Gunicorn
- Listens on port 8000
- Runs as a non-root user
- Includes a Docker health check

## 7. Build the Docker Image

Run:

```bash
sudo docker build -t clinicpulse:local .
```

Check the image:

```bash
sudo docker images
```

You should see an image named `clinicpulse`.

## 8. Configure the Simulation Token

ClinicPulse protects its incident simulation endpoints using a token.

Choose a strong token:

```bash
read -rsp "Enter a simulation token: " SIMULATION_TOKEN
echo
```

Keep this token private.

Never commit it to GitHub.

## 9. Run the Docker Container

Start ClinicPulse:

```bash
sudo docker run -d \
  --name clinicpulse-local \
  -p 127.0.0.1:8001:8000 \
  -e SIMULATION_TOKEN="$SIMULATION_TOKEN" \
  clinicpulse:local
```

Explanation:

- `-d` runs the container in the background.
- `--name` assigns a container name.
- `-p` maps the local port to the container port.
- `-e` passes the simulation token.
- `clinicpulse:local` is the Docker image.

The application is accessible only from the local machine.

## 10. Verify the Container

Run:

```bash
sudo docker ps
```

Check logs:

```bash
sudo docker logs clinicpulse-local
```

Check application health:

```bash
curl http://127.0.0.1:8001/health
```

Expected response:

```json
{
  "service": "ClinicPulse",
  "status": "UP"
}
```

## 11. Access the Dashboard

Open your browser:

http://127.0.0.1:8001

You should see the ClinicPulse monitoring dashboard.

If the application is running on a remote Ubuntu server, create an SSH tunnel from your computer:

```bash
ssh -i /path/to/key.pem \
  -L 8001:127.0.0.1:8001 \
  ubuntu@YOUR_SERVER_PUBLIC_IP
```

Then open:

http://localhost:8001

Do not expose the simulation controls directly to the public internet.

## 12. Test Service Monitoring

Check Appointment:

```bash
curl http://127.0.0.1:8001/services/appointments
```

Check Pharmacy:

```bash
curl http://127.0.0.1:8001/services/pharmacy
```

Check Laboratory:

```bash
curl http://127.0.0.1:8001/services/laboratory
```

Check the overall service status:

```bash
curl http://127.0.0.1:8001/api/status
```

## 13. Simulate a Service Failure

Bring Pharmacy DOWN:

```bash
curl -X POST \
  http://127.0.0.1:8001/simulate/pharmacy/down \
  -H "X-Simulation-Token: $SIMULATION_TOKEN"
```

Refresh the dashboard.

The Pharmacy service should show a failure.

## 14. Recover the Service

Restore Pharmacy:

```bash
curl -X POST \
  http://127.0.0.1:8001/simulate/pharmacy/up \
  -H "X-Simulation-Token: $SIMULATION_TOKEN"
```

Refresh the dashboard.

The service should return to UP.

This recovery changes simulated application state. It does not restart AWS infrastructure.

## 15. Amazon Bedrock Integration

ClinicPulse uses Amazon Bedrock Nova Micro for AI-assisted incident investigation.

This feature requires:

- AWS credentials
- Permission to invoke the Bedrock model
- Model availability in us-east-1

The AI receives service status and response-time information.

It suggests possible causes and troubleshooting steps.

AI-generated recommendations are not confirmed root causes.

The dashboard can run without using Bedrock.

To enable Bedrock inside a local Docker container, configure AWS authentication securely. Do not put AWS access keys in the Dockerfile or repository.

## 16. Run Automated Tests

Install Python tools:

```bash
sudo apt install python3-venv python3-pip -y
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
pip install pytest
```

Run tests:

```bash
python -m pytest -v
```

The project currently contains 19 automated tests.

## 17. Stop ClinicPulse

Stop the container:

```bash
sudo docker stop clinicpulse-local
```

Remove the container:

```bash
sudo docker rm clinicpulse-local
```

Remove the image if no longer needed:

```bash
sudo docker rmi clinicpulse:local
```

## 18. Troubleshooting

### Docker permission denied

Use `sudo` before Docker commands.

### Docker service not running

```bash
sudo systemctl restart docker
```

### Port already in use

Check:

```bash
sudo ss -lntp | grep 8001
```

Stop the conflicting application or choose another local port.

### Application not responding

Check:

```bash
sudo docker logs clinicpulse-local
```

### Simulation returns 403 Forbidden

Verify that the request contains the correct `X-Simulation-Token` header.

### AI investigation fails

Verify AWS authentication, IAM permissions, Bedrock model availability, and the application logs.

## 19. Security Notes

- Never publish simulation tokens.
- Never commit AWS credentials.
- Use SSH tunneling for remote local testing.
- Do not expose administrative endpoints over public HTTP.
- Use HTTPS and appropriate access controls for public deployments.

## Conclusion

You have successfully deployed ClinicPulse locally using Docker.

You have also learned how to:

- Install Docker
- Clone a GitHub repository
- Build a Docker image
- Run a container
- Check application health
- Simulate incidents
- Restore services
- View container logs
- Run automated tests

For cloud deployment, see [AWS Elastic Beanstalk Deployment](aws-deployment.md).
