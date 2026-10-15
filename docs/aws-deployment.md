# ☁️ ClinicPulse — AWS Elastic Beanstalk Deployment Guide

This guide explains how beginners can deploy ClinicPulse to their own AWS account.

We will cover two methods:

1. Manual deployment using AWS Elastic Beanstalk.
2. Automated deployment using GitHub Actions CI/CD.

The automated pipeline includes:

GitHub → Tests → Docker Build → Trivy → Docker Hub → AWS Elastic Beanstalk

## 1. Prerequisites

You need:

- AWS account
- GitHub account
- Docker Hub account
- Basic understanding of Git
- Internet connection
- Permission to configure AWS services

Recommended AWS Region:

`us-east-1`

This matches the original ClinicPulse deployment.

## 2. Understand AWS Elastic Beanstalk

AWS Elastic Beanstalk is a managed application deployment service.

It helps deploy applications without manually configuring every infrastructure component.

Depending on the environment, Elastic Beanstalk manages resources such as:

- EC2 instances
- Security groups
- Application deployment
- Health monitoring
- Load balancing

Elastic Beanstalk itself generally has no additional service charge, but the AWS resources it provisions can incur costs.

Create an AWS Budget alert before beginning.

---

# PART A — MANUAL DEPLOYMENT

## 3. Create a Docker Hub Account

Visit:

https://hub.docker.com/

Create an account.

Create a public repository named:

`clinicpulse`

Your repository will look like:

`YOUR_DOCKERHUB_USERNAME/clinicpulse`

## 4. Build the Docker Image

First, clone the project:

```bash
git clone https://github.com/akhilantotharayil/clinicpulse.git
cd clinicpulse
```

Build the image:

```bash
sudo docker build -t clinicpulse:local .
```

Tag it:

```bash
sudo docker tag clinicpulse:local \
  YOUR_DOCKERHUB_USERNAME/clinicpulse:latest
```

Replace `YOUR_DOCKERHUB_USERNAME` with your Docker Hub username.

## 5. Push the Image to Docker Hub

Log in:

```bash
sudo docker login -u YOUR_DOCKERHUB_USERNAME
```

Use a Docker Hub access token when prompted for authentication.

Push the image:

```bash
sudo docker push \
  YOUR_DOCKERHUB_USERNAME/clinicpulse:latest
```

Open Docker Hub and verify that the image exists.

## 6. Create Dockerrun.aws.json

Elastic Beanstalk needs to know which Docker image to run.

Create a deployment directory:

```bash
mkdir -p deployment
```

Create the file:

```bash
nano deployment/Dockerrun.aws.json
```

Add:

```json
{
  "AWSEBDockerrunVersion": "1",
  "Image": {
    "Name": "YOUR_DOCKERHUB_USERNAME/clinicpulse:latest"
  },
  "Ports": [
    {
      "ContainerPort": "8000"
    }
  ]
}
```

Replace the Docker Hub username.

Save the file.

## 7. Create the Deployment ZIP

Run:

```bash
cd deployment
zip ../clinicpulse-deploy.zip Dockerrun.aws.json
cd ..
```

If `zip` is unavailable:

```bash
sudo apt install zip -y
```

Verify:

```bash
unzip -l clinicpulse-deploy.zip
```

The ZIP should contain `Dockerrun.aws.json` at its root.

## 8. Prepare AWS IAM Roles

Elastic Beanstalk typically requires:

- An Elastic Beanstalk service role
- An EC2 instance profile

The service role allows Elastic Beanstalk to manage the environment.

The instance profile gives the application's EC2 instance its AWS permissions.

Open:

AWS Console → IAM → Roles

Create or select suitable roles following the current AWS Elastic Beanstalk documentation.

Use the AWS-managed Elastic Beanstalk policies appropriate for the selected environment.

Do not give the application administrator permissions.

For Amazon Bedrock, grant the EC2 instance role only the model invocation permissions it needs.

## 9. Create an Elastic Beanstalk Application

Open:

AWS Console → Elastic Beanstalk

Choose:

**Create application**

Enter an application name, for example:

`clinicpulse-demo`

Choose the Docker platform.

Select a supported platform version.

Create a web server environment.

Example environment name:

`clinicpulse-demo-env`

Select the previously configured service role and instance profile.

For learning, choose a small, single-instance environment where available.

Review the estimated AWS charges before proceeding.

## 10. Upload the Deployment Package

During application creation, select the option to upload application code.

Upload:

`clinicpulse-deploy.zip`

Alternatively, create the environment first and upload the package as a new application version.

Elastic Beanstalk will provision the required AWS resources and start the Docker image.

Wait for the environment to become healthy.

## 11. Access ClinicPulse

Elastic Beanstalk provides an environment URL.

Example:

`http://YOUR-ENVIRONMENT.us-east-1.elasticbeanstalk.com`

Open the URL in your browser.

You should see the ClinicPulse dashboard.

Check:

`http://YOUR-ENVIRONMENT.us-east-1.elasticbeanstalk.com/health`

The public HTTP URL is suitable for basic health verification, but do not send simulation tokens or use administrative controls over HTTP.

For secure administrative access, configure HTTPS and appropriate authentication.

## 12. Manual Deployment Complete

You have deployed ClinicPulse using:

Docker → Docker Hub → AWS Elastic Beanstalk

Next, we will automate the process.

---

# PART B — AUTOMATED CI/CD DEPLOYMENT

## 13. Understand the Pipeline

ClinicPulse uses GitHub Actions.

The existing workflow performs:

1. Automated Python tests.
2. Docker image build.
3. Container smoke testing.
4. Trivy vulnerability scanning.
5. Docker image publishing.
6. AWS authentication using GitHub OIDC.
7. Elastic Beanstalk deployment.
8. Deployment health verification.

The Trivy scan currently reports HIGH and CRITICAL findings but does not fail the pipeline because its exit code is configured as `0`.

## 14. Fork the Repository

Open:

https://github.com/akhilantotharayil/clinicpulse

Click **Fork**.

Create a copy under your GitHub account.

Clone your fork:

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/clinicpulse.git
cd clinicpulse
```

## 15. Prepare Your AWS Environment

Complete the manual deployment steps first.

You should have:

- An Elastic Beanstalk application
- An Elastic Beanstalk environment
- A suitable EC2 instance profile
- A Docker Hub repository
- An S3 bucket for deployment packages

Record the following values:

```text
AWS_REGION=us-east-1

AWS_ACCOUNT_ID=YOUR_AWS_ACCOUNT_ID

EB_APPLICATION_NAME=YOUR_APPLICATION_NAME

EB_ENVIRONMENT_NAME=YOUR_ENVIRONMENT_NAME

S3_BUCKET=YOUR_DEPLOYMENT_BUCKET

DOCKERHUB_USERNAME=YOUR_DOCKERHUB_USERNAME
```

These values are different for every AWS account.

## 16. Configure GitHub OIDC

GitHub OIDC allows GitHub Actions to assume an AWS IAM role without storing permanent AWS access keys.

Open:

AWS Console → IAM → Identity Providers

Add an OpenID Connect provider if one is not already configured.

Provider URL:

`https://token.actions.githubusercontent.com`

Audience:

`sts.amazonaws.com`

Follow the current AWS documentation for creating the provider.

## 17. Create an IAM Role for GitHub Actions

Open:

IAM → Roles → Create role

Choose the GitHub OIDC provider.

Restrict the role to your repository and main branch.

Example trust policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::YOUR_AWS_ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:YOUR_GITHUB_USERNAME/clinicpulse:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

Replace:

- `YOUR_AWS_ACCOUNT_ID`
- `YOUR_GITHUB_USERNAME`

This example permits deployments from the specified repository's main branch.

## 18. Configure IAM Permissions

The GitHub Actions IAM role needs permissions to:

- Upload deployment packages to its designated S3 location.
- Read Elastic Beanstalk application versions.
- Create Elastic Beanstalk application versions.
- Update the designated Elastic Beanstalk environment.
- Describe the environment and verify deployment status.

Grant the minimum permissions required.

Some Elastic Beanstalk deployment operations require additional permissions depending on the AWS configuration.

Avoid granting broad administrator access.

## 19. Configure GitHub Secrets

Open your fork:

GitHub → Settings → Secrets and variables → Actions

Add repository secrets:

```text
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
AWS_ROLE_ARN
```

`DOCKERHUB_USERNAME` is your Docker Hub username.

`DOCKERHUB_TOKEN` is a Docker Hub access token with the required repository permissions.

`AWS_ROLE_ARN` is the IAM role created for GitHub OIDC.

Example role ARN:

```text
arn:aws:iam::YOUR_AWS_ACCOUNT_ID:role/YOUR_GITHUB_DEPLOY_ROLE
```

Never commit credentials or access tokens to GitHub.

## 20. Update the Existing GitHub Actions Workflow

Open the workflow:

```bash
nano .github/workflows/ci.yml
```

The original workflow contains values specific to the original ClinicPulse deployment.

You must replace them with your own values.

### Docker Hub Image

Original:

```text
akhilanto/clinicpulse
```

Replace with:

```text
YOUR_DOCKERHUB_USERNAME/clinicpulse
```

Update every image reference, including:

- Docker tagging
- Docker pushing
- Dockerrun.aws.json generation

### AWS Account and S3 Bucket

Replace the original deployment bucket with your own S3 bucket.

For example:

```text
s3://YOUR_DEPLOYMENT_BUCKET/clinicpulse-deployments/
```

Also update the S3 bucket and object key supplied to the Elastic Beanstalk `create-application-version` command.

### Elastic Beanstalk Application

Replace:

```text
clinicpulse
```

With your own application name wherever the workflow uses:

```bash
--application-name
```

### Elastic Beanstalk Environment

Replace:

```text
clinicpulse-blue
```

With your environment name wherever the workflow uses:

```bash
--environment-name
```

Or:

```bash
--environment-names
```

### AWS Region

The original workflow uses:

```text
us-east-1
```

If deploying elsewhere, update all region references and verify that required AWS services are available.

### Workflow Permissions

The deployment job must include:

```yaml
permissions:
  contents: read
  id-token: write
```

This allows GitHub Actions to request an OIDC token.

## 21. Understand Image Versioning

The existing workflow publishes images with two tags:

```text
YOUR_DOCKERHUB_USERNAME/clinicpulse:latest
```

And:

```text
YOUR_DOCKERHUB_USERNAME/clinicpulse:GITHUB_COMMIT_SHA
```

The commit SHA identifies the exact image associated with a deployment.

Elastic Beanstalk uses the commit-specific image tag.

This makes deployments more traceable than relying only on `latest`.

## 22. Push Your Workflow Changes

After updating the workflow:

```bash
git add .github/workflows/ci.yml
```

Commit:

```bash
git commit -m "Configure CI/CD for my AWS environment"
```

Push:

```bash
git push origin main
```

## 23. Monitor GitHub Actions

Open:

GitHub → Actions

Select:

**ClinicPulse CI/CD**

The workflow should run automatically.

Expected jobs:

```text
Flask Automated Tests
        |
        v
Build and Test Docker Image
        |
        v
Publish to Docker Hub
        |
        v
Deploy to AWS Elastic Beanstalk
```

A pull request runs the testing and image-build jobs but does not publish or deploy.

Publishing and deployment occur on pushes to `main`.

## 24. Verify Deployment

After the workflow succeeds:

Open:

AWS Console → Elastic Beanstalk → Environments

Select your environment.

Verify that:

- Environment status is Ready.
- Health is Green.
- The expected application version is deployed.

Open the environment URL.

Verify:

```text
/health
```

The application should report an UP status.

## 25. Configure CloudWatch Monitoring

Open:

AWS Console → CloudWatch

Review the metrics available for your Elastic Beanstalk environment and underlying EC2 resources.

Depending on your environment configuration, these may include:

- CPU utilization
- EC2 instance status
- Environment health information
- Request and latency metrics

Not every metric is available in every Elastic Beanstalk configuration.

Create alarms for metrics appropriate to your environment.

For example, create an EC2 CPU utilization alarm using a threshold and evaluation period suitable for your application.

## 26. Configure Amazon SNS Notifications

Open:

AWS Console → Amazon SNS

Create a topic.

Example:

`clinicpulse-alerts`

Create an email subscription.

Confirm the subscription using the verification email.

Open CloudWatch.

Create or edit an alarm.

Configure the alarm action to publish notifications to the SNS topic.

When the alarm enters its configured state, SNS can send an email notification.

Note that ClinicPulse's simulated service failures do not automatically guarantee that an EC2 or Elastic Beanstalk infrastructure alarm will fire.

## 27. Configure Amazon Bedrock

ClinicPulse uses:

`amazon.nova-micro-v1:0`

AWS Region:

`us-east-1`

To enable AI investigation:

1. Open Amazon Bedrock.
2. Confirm the model is available to your account.
3. Configure the required model access or invocation permissions.
4. Grant the Elastic Beanstalk EC2 instance role permission to invoke the model.
5. Verify the application can authenticate through the instance role.

Avoid storing permanent AWS access keys in the application.

Bedrock requests may incur charges.

The AI receives service status and response-time information, not CloudWatch logs or infrastructure metrics.

## 28. Configure Simulation Security

ClinicPulse uses the `SIMULATION_TOKEN` environment variable.

Configure a strong value through Elastic Beanstalk environment properties or an appropriate secrets-management integration.

Do not commit the token.

Do not transmit the token over public HTTP.

Before exposing administrative controls publicly, configure HTTPS and appropriate access restrictions.

For a public hackathon demonstration, basic read-only dashboard access is preferable to exposing incident simulation controls.

## 29. Troubleshooting

### GitHub Actions OIDC authentication fails

Verify:

- AWS role ARN
- GitHub repository name
- Branch name
- IAM trust policy
- OIDC provider
- IAM permissions

### Docker Hub push fails

Verify:

- Docker Hub username
- Docker Hub access token
- Repository name
- Token permissions

### Elastic Beanstalk deployment fails

Check:

- Application name
- Environment name
- AWS Region
- S3 bucket
- IAM permissions
- Deployment package contents

### Environment health is not Green

Check:

- Elastic Beanstalk events
- EC2 instance logs
- Docker container logs
- Application health endpoint
- Port configuration

### Bedrock invocation fails

Verify:

- Model availability
- IAM permissions
- AWS Region
- Instance role
- Application logs

## 30. AWS Cost Management and Cleanup

AWS resources may continue generating charges after you finish testing.

When the project is no longer needed:

1. Open Elastic Beanstalk.
2. Terminate the test environment.
3. Verify that associated EC2 instances and other provisioned resources have been removed.
4. Delete unnecessary deployment artifacts from S3.
5. Remove unused CloudWatch alarms.
6. Delete unused SNS topics and subscriptions.
7. Review other resources created for the deployment.
8. Check AWS Billing and Cost Management.

Be careful not to delete resources used by other projects.

## Conclusion

You have learned two deployment methods.

### Manual Deployment

```text
Source Code
     |
     v
Docker Build
     |
     v
Docker Hub
     |
     v
AWS Elastic Beanstalk
     |
     v
ClinicPulse Dashboard
```

### Automated CI/CD Deployment

```text
GitHub Push
     |
     v
Automated Tests
     |
     v
Docker Build
     |
     v
Container Smoke Test
     |
     v
Trivy Security Scan
     |
     v
Docker Hub
     |
     v
GitHub OIDC Authentication
     |
     v
S3 Deployment Package
     |
     v
AWS Elastic Beanstalk
     |
     v
Deployment Verification
```

You can now deploy ClinicPulse locally or to AWS Elastic Beanstalk.

For local deployment instructions, see [Local Deployment](local-deployment.md).

For the complete project architecture, see [Architecture](architecture.md).
