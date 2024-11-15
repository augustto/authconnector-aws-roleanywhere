import os
import configparser
import subprocess
import json

def get_temporary_credentials(cert_path, key_path, role_arn, profile_arn, trust_anchor_arn, region='us-east-1'):
    # Executes the aws_signing_helper command to obtain temporary credentials using IAM Roles Anywhere
    command = [
        "aws_signing_helper",
        "credential-process",
        "--certificate", cert_path,
        "--private-key", key_path,  
        "--trust-anchor-arn", trust_anchor_arn,
        "--profile-arn", profile_arn,
        "--role-arn", role_arn,
        "--region", region
    ]
    
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error while retrieving credentials: {result.stderr}")
        return None
    
    # Parse the JSON result to extract the credentials
    credentials = json.loads(result.stdout)
    return credentials

def update_aws_credentials(credentials, profile='default'):
    # Updates the ~/.aws/credentials file with the temporary credentials
  
    credentials_path = os.path.expanduser('~/.aws/credentials')
    config = configparser.ConfigParser()
    config.read(credentials_path)
    
    if profile not in config:
        config.add_section(profile)
    
    # Update the credentials in the specified profile
    config[profile]['aws_access_key_id'] = credentials['AccessKeyId']
    config[profile]['aws_secret_access_key'] = credentials['SecretAccessKey']
    config[profile]['aws_session_token'] = credentials['SessionToken']
    
    with open(credentials_path, 'w') as configfile:
        config.write(configfile)
    
    print(f"Credentials updated for profile '{profile}' in the file {credentials_path}.")

# IAM Roles Anywhere Configuration
cert_path = "./clientEntity.pem"
key_path = "./clientEntity.key"  
role_arn = "arn:aws:iam::<account-id>:role/<role-name>"
profile_arn = "arn:aws:rolesanywhere:<region>:<account-id>:profile/<profile-id>"
trust_anchor_arn = "arn:aws:rolesanywhere:<region>:<account-id>:trust-anchor/<trust-anchor-id>"

# Retrieve temporary credentials
credentials = get_temporary_credentials(cert_path, key_path, role_arn, profile_arn, trust_anchor_arn, 'us-east-1')

# If credentials were successfully obtained, update the credentials file
if credentials:
    update_aws_credentials(credentials)
else:
    print("Unable to obtain temporary credentials.")
