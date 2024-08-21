import boto3
import botocore.exceptions
from concurrent.futures import ThreadPoolExecutor, as_completed

# Function to assume a role in a different AWS account
def assume_role(account_id, role_name):
  
    # Assumes an IAM role in the specified AWS account and returns temporary credentials.
    try:
        # Initialize STS client to assume the role
        client = boto3.client('sts')
        response = client.assume_role(
            RoleArn=f"arn:aws:iam::{account_id}:role/{role_name}",
            RoleSessionName="CrossAccountSession"
        )
        print(f"[INFO] Successfully assumed role in account {account_id}")
        # Return the assumed role credentials
        return response['Credentials']
    
    except botocore.exceptions.ClientError as e:
        print(f"[ERROR] Failed to assume role in account {account_id}. Error: {e}")
        return None

# Function to list all A records in a Route 53 hosted zone
def get_a_records(credentials):
    """
    Retrieves A records from Route 53 hosted zones using the provided credentials.
    """
    if not credentials:
        return []  # Early return if no credentials provided

    try:
        # Create a session using the temporary credentials
        session = boto3.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
        )
        route53 = session.client('route53')

        # Fetch the list of hosted zones
        hosted_zones = route53.list_hosted_zones()['HostedZones']

        a_records = []
        for zone in hosted_zones:
            zone_id = zone['Id']
            try:
                # Retrieve all resource record sets (DNS records) in the hosted zone
                records = route53.list_resource_record_sets(HostedZoneId=zone_id)
                for record in records['ResourceRecordSets']:
                    if record['Type'] == 'A':  # Only consider A records
                        a_records.append((record['Name'], record['ResourceRecords']))
            
            except botocore.exceptions.ClientError as e:
                print(f"[ERROR] Failed to list records for hosted zone {zone_id}. Error: {e}")

        print(f"[INFO] Retrieved {len(a_records)} A records from account")
        return a_records

    except botocore.exceptions.ClientError as e:
        print(f"[ERROR] Failed to create Route 53 client or list hosted zones. Error: {e}")
        return []

# Function to get all AWS account IDs in an organization
def get_all_accounts():

    #Retrieves all AWS account IDs in the current organization.
    accounts = []
    try:
        org_client = boto3.client('organizations')
        paginator = org_client.get_paginator('list_accounts')
        
        # Use pagination to handle large numbers of accounts
        for page in paginator.paginate():
            for account in page['Accounts']:
                if account['Status'] == 'ACTIVE':  # Filter only active accounts
                    accounts.append(account['Id'])
                    
    except botocore.exceptions.ClientError as e:
        print(f"[ERROR] Failed to list accounts. Error: {e}")
    
    print(f"[INFO] Found {len(accounts)} active accounts in the organization")
    return accounts

# AWS Lambda handler
def lambda_handler(event, context):
    """
    Main Lambda function handler. Retrieves and processes A records from all accounts in the organization.
    """
    role_name = "user-role-here"  # Enter the role to assume in each account

    # Automatically populate the accounts list with IDs from AWS Organizations
    account_ids = get_all_accounts()

    results = []  # To store the results for processing or logging

    # Use ThreadPoolExecutor for parallel processing of accounts
    with ThreadPoolExecutor(max_workers=10) as executor:  # Adjust max_workers based on expected load
        future_to_account = {executor.submit(assume_and_fetch, account_id, role_name): account_id for account_id in account_ids}

        # Collect results as they are completed
        for future in as_completed(future_to_account):
            account_id = future_to_account[future]
            try:
                a_records = future.result()
                if a_records:
                    for domain, ips in a_records:
                        result = {
                            "AccountID": account_id,
                            "Domain": domain,
                            "IPs": ips
                        }
                        results.append(result)
                        # Log or process the results as needed
                        print(f"[INFO] Account {account_id}: Processed domain {domain} with IPs {ips}")
            except Exception as e:
                print(f"[ERROR] Account {account_id} generated an exception: {e}")

    print(f"[INFO] Completed processing {len(account_ids)} accounts")
    return results  # Optionally return the results for further processing or logging

def assume_and_fetch(account_id, role_name):

    # Helper function to assume role and fetch A records. Runs in parallel using ThreadPoolExecutor.
    credentials = assume_role(account_id, role_name)
    if credentials:
        return get_a_records(credentials)
    return []

