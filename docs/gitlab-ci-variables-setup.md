# Setting Up GitLab CI/CD Variables

This document explains how to securely set up environment variables in GitLab CI/CD for the Plumber Leads application.

## Required Variables

The following variables need to be set up in GitLab CI/CD:

### Database Configuration
- `DATABASE_URL`: PostgreSQL connection string
- `SQLALCHEMY_DATABASE_URI`: SQLAlchemy connection string

### Supabase Configuration
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_KEY`: Supabase API key

### Admin User Configuration
- `ADMIN_PW`: Password for the admin user (will be set as ADMIN_PASSWORD in the environment)

### Server Configuration
- `SERVER_IP`: IP address of the deployment server
- `SERVER_USER`: SSH username for the deployment server
- `SSH_PRIVATE_KEY`: SSH private key for server access
- `SSH_KNOWN_HOSTS`: SSH known hosts file content

### Application Configuration
- `SECRET_KEY`: Flask application secret key
- `DB_PASSWORD`: Database password for the deployed application

## Setting Up Variables in GitLab

1. **Navigate to GitLab CI/CD Variables**:
   - Go to your GitLab project
   - Click on **Settings > CI/CD**
   - Expand the **Variables** section

2. **Add Each Variable**:
   - Click on **Add Variable**
   - Enter the variable name (e.g., `DATABASE_URL`)
   - Enter the variable value
   - Configure protection options:
     - **Protect variable**: Enable this for sensitive variables to limit them to protected branches
     - **Mask variable**: Enable this for all sensitive variables to hide them in job logs
   - Click **Add Variable**

3. **Variable Protection**:
   - For production credentials, enable the "Protected" option
   - This ensures the variables are only available in protected branches (like `main` or `production`)

## Security Best Practices

1. **Mask Sensitive Variables**:
   - Always mask variables containing passwords, tokens, or keys
   - This prevents them from appearing in job logs

2. **Use Protected Variables**:
   - Mark variables as protected when they contain sensitive production data
   - This restricts their use to protected branches only

3. **Rotate Credentials**:
   - Regularly rotate sensitive credentials
   - Update the GitLab CI/CD variables after rotation

4. **Limit Access**:
   - Only GitLab administrators and project maintainers can view or modify CI/CD variables
   - Restrict maintainer access to trusted team members

## Troubleshooting

If your deployment is failing due to missing environment variables:

1. Check that all required variables are set in GitLab CI/CD
2. Verify that the variable names match exactly what's expected in the scripts
3. For protected variables, ensure you're running the pipeline on a protected branch
4. Check the job logs for any error messages related to missing variables

## Advanced: Using External Secrets Managers

For enhanced security, consider using an external secrets manager:

1. **HashiCorp Vault**:
   - GitLab has native integration with HashiCorp Vault
   - See [GitLab Vault Integration](https://docs.gitlab.com/ee/ci/secrets/index.html) for setup

2. **AWS Secrets Manager or Azure Key Vault**:
   - Can be integrated using custom scripts in your CI/CD pipeline

## References

- [GitLab CI/CD Variables Documentation](https://docs.gitlab.com/ee/ci/variables/)
- [GitLab CI/CD Pipeline Security](https://docs.gitlab.com/ee/ci/pipelines/pipeline_security.html) 