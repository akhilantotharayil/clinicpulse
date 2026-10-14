# ClinicPulse — AWS Architecture

```mermaid
flowchart TB
    DEV["Developer"] --> GH["GitHub Repository"]

    GH --> CI["GitHub Actions CI/CD"]

    CI --> TEST["Automated Tests"]
    CI --> BUILD["Docker Build"]
    CI --> SCAN["Trivy Security Scan"]

    BUILD --> HUB["Docker Hub"]
    HUB --> EB["AWS Elastic Beanstalk"]

    CI -->|OIDC Deployment| EB

    subgraph AWS["AWS Cloud"]
        EB --> APP["Dockerized Flask Application"]

        APP --> APT["Appointment Service"]
        APP --> PHA["Pharmacy Service"]
        APP --> LAB["Laboratory Service"]

        APP --> AIAPI["AI Investigation API"]
        AIAPI --> BEDROCK["Amazon Bedrock — Nova Micro"]

        APP --> CW["Amazon CloudWatch"]
        CW --> ALARM["CloudWatch Alarms"]
        ALARM --> SNS["Amazon SNS"]
    end

    USER["Dashboard Viewer"] -->|HTTP Read-only| EB
```

## Architecture Notes

- GitHub Actions automates testing, image creation, security scanning, publishing, and deployment.
- Docker Hub stores the application container image.
- Elastic Beanstalk runs the Dockerized Flask application.
- Appointment, Pharmacy, and Laboratory are simulated endpoints within the Flask application.
- Amazon Bedrock Nova Micro generates AI-assisted incident investigation reports.
- Amazon CloudWatch collects monitoring metrics.
- CloudWatch alarms can trigger Amazon SNS notifications.
- The public HTTP dashboard is intended for read-only viewing until HTTPS is configured.
